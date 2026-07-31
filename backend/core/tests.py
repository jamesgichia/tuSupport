from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Organization, Membership
from django.test import override_settings
from unittest.mock import patch


User = get_user_model()


@override_settings(REST_FRAMEWORK={
    'DEFAULT_THROTTLE_RATES': {
        'login': '100/minute',
        'anon': '100/minute',
    }
})



class LoginResponseTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='james', password='testpass123'
        )
        self.org = Organization.objects.create(name='Test Org')
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.ADMIN
        )

    def test_login_returns_org_list(self):
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('organizations', response.data)
        self.assertEqual(len(response.data['organizations']), 1)
        self.assertEqual(response.data['organizations'][0]['name'], 'Test Org')
        self.assertEqual(response.data['organizations'][0]['role'], 'admin')

    def test_login_sets_httponly_refresh_cookie(self):
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)

        # Refresh token must NOT be in the JSON body — frontend should never see it
        self.assertNotIn('refresh', response.data)

        # Cookie must exist
        self.assertIn('refresh_token', response.cookies)

        cookie = response.cookies['refresh_token']

        # HttpOnly closes the XSS theft vector
        self.assertTrue(cookie['httponly'])

        # SameSite=Strict closes the CSRF vector
        self.assertEqual(cookie['samesite'], 'Strict')

        # Cookie scoped to all auth endpoints — covers refresh and logout
        self.assertEqual(cookie['path'], '/api/v1/auth/')

    def test_refresh_endpoint_reads_cookie_and_returns_new_access_token(self):
        # Step 1 — login to get the cookie planted
        login_response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })
        self.assertEqual(login_response.status_code, 200)

        # Step 2 — call refresh with empty body; APIClient carries the cookie automatically
        refresh_response = self.client.post('/api/v1/auth/token/refresh/')
        self.assertEqual(refresh_response.status_code, 200)

        # New access token must be present
        self.assertIn('access', refresh_response.data)

        # Rotated refresh token must be set as a new cookie
        self.assertIn('refresh_token', refresh_response.cookies)

        # Refresh token must still not appear in the JSON body
        self.assertNotIn('refresh', refresh_response.data)


@override_settings(REST_FRAMEWORK={
		'DEFAULT_THROTTLE_RATES': {
				'login': '100/minute',
				'anon': '100/minute',
		}
})


class MembershipPrivilegeEscalationTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.admin_user = User.objects.create_user(
            username='admin_user', password='pass123'
        )
        self.member_user = User.objects.create_user(
            username='member_user', password='pass123'
        )
        Membership.objects.create(
            user=self.admin_user, organization=self.org, role='admin'
        )
        self.member_membership = Membership.objects.create(
            user=self.member_user, organization=self.org, role='member'
        )
        self.client = APIClient()

    def test_member_cannot_escalate_own_role(self):
        """A member attempting to set their own role to admin must be blocked."""
        self.client.force_authenticate(user=self.member_user)
        url = f'/api/v1/organizations/{self.org.id}/memberships/{self.member_membership.id}/'
        response = self.client.patch(url, {'role': 'admin'}, format='json')
        # Must be rejected — never 200
        self.assertNotEqual(response.status_code, 200)
        # Confirm the DB was not mutated
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, 'member')

    def test_admin_can_change_member_role(self):
        """An admin promoting a member is a legitimate operation."""
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/v1/organizations/{self.org.id}/memberships/{self.member_membership.id}/'
        response = self.client.patch(url, {'role': 'admin'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, 'admin')



class LogoutTest(TestCase):
    def setUp(self):
        self.throttle_patcher = patch(
            'core.throttles.LoginRateThrottle.allow_request',
            return_value=True
        )
        self.throttle_patcher.start()

        self.client = APIClient()
        self.user = User.objects.create_user(
            username='james', password='testpass123'
        )
        self.org = Organization.objects.create(name='Test Org')
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.ADMIN
        )

    def tearDown(self):
        self.throttle_patcher.stop()


    def _login(self):
        """Helper — logs in and returns the access token."""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        return response.data['access']

    def test_logout_blacklists_refresh_token(self):
        # Step 1 — login, cookie is planted automatically
        access = self._login()

        # Step 2 — logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)

        # Step 3 — attempt token refresh — must be rejected
        refresh_response = self.client.post('/api/v1/auth/token/refresh/')
        self.assertEqual(refresh_response.status_code, 401)

    def test_logout_clears_cookie(self):
        # Login to plant the cookie
        access = self._login()

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)

        # Cookie must be cleared — max-age 0 or empty value signals deletion
        cookie = response.cookies.get('refresh_token')
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, '')

    def test_logout_requires_authentication(self):
        # Unauthenticated POST to logout must be rejected
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 401)

    def test_logout_without_cookie_returns_400(self):
        # Authenticated user but no refresh cookie — e.g. cookie already expired
        access = self._login()

        # Manually clear the cookie before calling logout
        self.client.cookies.clear()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 400)
