from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Organization, Membership
from fundraisers.models import Fundraiser
from core.throttles import LoginRateThrottle
from unittest.mock import patch


User = get_user_model()

class IDORFundraiserTest(TestCase):
    """
    Proves that a user from Org A cannot see Org B's fundraisers.
    This test is expected to FAIL before TenantManager is fixed.
    """

    def setUp(self):
        # --- Org A setup ---
        self.org_a = Organization.objects.create(name="Org A")
        self.user_a = User.objects.create_user(username="user_a", password="pass_a")
        Membership.objects.create(user=self.user_a, organization=self.org_a, role="admin")

        # --- Org B setup ---
        self.org_b = Organization.objects.create(name="Org B")
        self.user_b = User.objects.create_user(username="user_b", password="pass_b")
        Membership.objects.create(user=self.user_b, organization=self.org_b, role="admin")

        # --- Org B's fundraiser (user_a should never see this) ---
        self.fundraiser_b = Fundraiser._base_manager.create(
            organization=self.org_b,
            title="Org B Secret Campaign",
            goal_amount=100000,
            status="published",
        )

    def test_user_cannot_see_other_org_fundraisers(self):
        # Log in as user_a and get a token
        client = APIClient()
        response = client.post("/api/v1/auth/token/", {
            "username": "user_a",
            "password": "pass_a"
        })
        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # user_a hits the fundraiser list
        response = client.get(f"/api/v1/organizations/{self.org_a.id}/fundraisers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract IDs from response
        returned_ids = [f["id"] for f in response.data]

        # THE SECURITY ASSERTION: Org B's fundraiser must not appear
        self.assertNotIn(
            self.fundraiser_b.id,
            returned_ids,
            "IDOR vulnerability: Org A user can see Org B's fundraiser"
        )


    def test_user_cannot_create_fundraiser_in_org_they_dont_belong_to(self):
        """Adversarial test: user_a belongs to org_a only.
        Attempt to POST a fundraiser via org_b's URL.
        Expected (once fixed): 404 — server refuses, nothing created.
        """
        client = APIClient()
        response = client.post("/api/v1/auth/token/", {
            "username": "user_a",
            "password": "pass_a"
        })
        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.post(
            f"/api/v1/organizations/{self.org_b.id}/fundraisers/",
            {"title": "Malicious Fundraiser", "goal_amount": 1000},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(
            Fundraiser.objects.filter(
                organization=self.org_b, title="Malicious Fundraiser"
            ).exists()
        )


class LoginThrottleTest(TestCase):
    """
    Proves the login endpoint blocks brute force attempts.
    5 attempts allowed per minute — 6th must return 429.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="throttle_user", password="correct_pass"
        )

    def test_sixth_login_attempt_is_blocked(self):
        # 5 allowed attempts (wrong password — we're simulating brute force)
        for _ in range(5):
            self.client.post("/api/v1/auth/token/", {
                "username": "throttle_user",
                "password": "wrong_pass"
            })

        # 6th attempt — must be blocked regardless of credentials
        response = self.client.post("/api/v1/auth/token/", {
            "username": "throttle_user",
            "password": "correct_pass"
        })

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)




class RolePermissionTest(TestCase):

    def setUp(self):
        # Disable throttling for role tests — throttle behavior
        # is tested separately in LoginThrottleTest
        self.throttle_patcher = patch(
            'core.throttles.LoginRateThrottle.allow_request',
            return_value=True
        )
        self.throttle_patcher.start()

        self.client = APIClient()
        self.org = Organization.objects.create(name="Test Org")

        self.admin = User.objects.create_user(
            username="admin_user", password="pass"
        )
        Membership.objects.create(
            user=self.admin, organization=self.org, role="admin"
        )

        self.member = User.objects.create_user(
            username="plain_member", password="pass"
        )
        Membership.objects.create(
            user=self.member, organization=self.org, role="member"
        )

    def tearDown(self):
        # Always stop the patcher — never leave mocks running
        self.throttle_patcher.stop()
