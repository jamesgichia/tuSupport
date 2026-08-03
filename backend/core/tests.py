from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from core.models import Organization, Membership
from core.throttles import LoginRateThrottle
from django.test import override_settings
from django.urls import reverse
from unittest.mock import patch
from django.core.cache import cache
from tusupport import settings

User = get_user_model()


# ─── Shared throttle bypass settings (for tests that are NOT testing throttling) ───

THROTTLE_DISABLED = {
    **settings.REST_FRAMEWORK,
    'DEFAULT_THROTTLE_RATES': {
        'login': '100/minute',
        'anon': '100/minute',
    }
}


# ─────────────────────────────────────────────────────────────────────────────────
# LOGIN & TOKEN TESTS
# ─────────────────────────────────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK=THROTTLE_DISABLED)
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
        self.assertNotIn('refresh', response.data)
        self.assertIn('refresh_token', response.cookies)

        cookie = response.cookies['refresh_token']
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Strict')
        self.assertEqual(cookie['path'], '/api/v1/auth/')

    def test_refresh_endpoint_reads_cookie_and_returns_new_access_token(self):
        login_response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })
        self.assertEqual(login_response.status_code, 200)

        refresh_response = self.client.post('/api/v1/auth/token/refresh/')
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn('access', refresh_response.data)
        self.assertIn('refresh_token', refresh_response.cookies)
        self.assertNotIn('refresh', refresh_response.data)


# ─────────────────────────────────────────────────────────────────────────────────
# THROTTLE TESTS
# ─────────────────────────────────────────────────────────────────────────────────

class LoginThrottleTest(APITestCase):

    def setUp(self):
        cache.clear()
        # Patch the rate directly on the throttle class
        self.rate_patcher = patch.object(
            LoginRateThrottle,
            'THROTTLE_RATES',
            {'login': '3/minute'}
        )
        self.rate_patcher.start()

        # Create a real user — throttle fires regardless of auth success/failure
        # but SimpleJWT still needs a valid DB to not crash earlier
        self.user = User.objects.create_user(
            username='throttle_user', password='testpass123'
        )
        self.org = Organization.objects.create(name='Throttle Org')
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.ADMIN
        )

    def tearDown(self):
        self.rate_patcher.stop()
        cache.clear()

    def test_login_throttle_returns_429_after_limit(self):
        url = '/api/v1/auth/token/'
        payload = {'username': 'attacker', 'password': 'wrongpassword'}

        for _ in range(3):
            self.client.post(url, payload)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 429)


class TokenRefreshThrottleTest(APITestCase):

    def setUp(self):
        cache.clear()
        self.rate_patcher = patch.object(
            LoginRateThrottle,
            'THROTTLE_RATES',
            {'login': '3/minute'}
        )
        self.rate_patcher.start()

        self.user = User.objects.create_user(
            username='refresh_throttle_user', password='testpass123'
        )
        self.org = Organization.objects.create(name='Throttle Org')
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.ADMIN
        )

    def tearDown(self):
        self.rate_patcher.stop()
        cache.clear()

    def test_refresh_throttle_returns_429_after_limit(self):
        # Step 1 — real login to plant valid cookie
        login = self.client.post('/api/v1/auth/token/', {
            'username': 'refresh_throttle_user',
            'password': 'testpass123'
        })
        self.assertEqual(login.status_code, 200)

        # Step 2 — exhaust the throttle on the refresh endpoint
        url = '/api/v1/auth/token/refresh/'
        for _ in range(3):
            self.client.post(url)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 429)

# ─────────────────────────────────────────────────────────────────────────────────
# MEMBERSHIP PRIVILEGE ESCALATION TESTS
# ─────────────────────────────────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK=THROTTLE_DISABLED)
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
        self.client.force_authenticate(user=self.member_user)
        url = f'/api/v1/organizations/{self.org.id}/memberships/{self.member_membership.id}/'
        response = self.client.patch(url, {'role': 'admin'}, format='json')
        self.assertNotEqual(response.status_code, 200)
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, 'member')

    def test_admin_can_change_member_role(self):
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/v1/organizations/{self.org.id}/memberships/{self.member_membership.id}/'
        response = self.client.patch(url, {'role': 'admin'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, 'admin')


# ─────────────────────────────────────────────────────────────────────────────────
# LOGOUT TESTS
# ─────────────────────────────────────────────────────────────────────────────────

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
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'james',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        return response.data['access']

    def test_logout_blacklists_refresh_token(self):
        access = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)
        refresh_response = self.client.post('/api/v1/auth/token/refresh/')
        self.assertEqual(refresh_response.status_code, 401)

    def test_logout_clears_cookie(self):
        access = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)
        cookie = response.cookies.get('refresh_token')
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, '')

    def test_logout_requires_authentication(self):
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 401)

    def test_logout_without_cookie_returns_400(self):
        access = self._login()
        self.client.cookies.clear()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 400)
