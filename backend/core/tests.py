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
