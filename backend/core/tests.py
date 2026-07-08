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
