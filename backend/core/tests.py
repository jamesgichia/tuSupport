from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Organization, Membership

User = get_user_model()


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

        # Cookie must be scoped to the refresh endpoint only — not the whole site
        self.assertEqual(cookie['path'], '/api/v1/auth/token/refresh/')

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
