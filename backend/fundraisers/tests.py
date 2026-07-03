from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Organization, Membership
from fundraisers.models import Fundraiser

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
        response = client.get("/api/v1/fundraisers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract IDs from response
        returned_ids = [f["id"] for f in response.data]

        # THE SECURITY ASSERTION: Org B's fundraiser must not appear
        self.assertNotIn(
            self.fundraiser_b.id,
            returned_ids,
            "IDOR vulnerability: Org A user can see Org B's fundraiser"
        )
