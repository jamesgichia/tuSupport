from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Organization, Membership
from fundraisers.models import Fundraiser, Contribution
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


class FundraiserDetailIDORTest(TestCase):
    def setUp(self):
        # Org A — legitimate owner
        self.org_a = Organization.objects.create(name="Org A")
        self.user_a = User.objects.create_user(
            username='user_a', password='pass123'
        )
        Membership.objects.create(
            user=self.user_a, organization=self.org_a, role='admin'
        )
        self.fundraiser = Fundraiser.objects.create(
            organization=self.org_a,
            title="Org A Fundraiser",
            description="Private to Org A",
            goal_amount=10000,
            status='draft'
        )

        # Org B — the attacker
        self.org_b = Organization.objects.create(name="Org B")
        self.user_b = User.objects.create_user(
            username='user_b', password='pass123'
        )
        Membership.objects.create(
            user=self.user_b, organization=self.org_b, role='member'
        )
        self.client = APIClient()

    def test_user_cannot_access_other_org_fundraiser(self):
        """
        User B must not be able to read User A's fundraiser —
        even if they know the fundraiser ID.
        Correct response is 404 — never 200, never 403.
        404 denies resource existence; 403 confirms it.
        """
        self.client.force_authenticate(user=self.user_b)
        url = f'/api/v1/organizations/{self.org_a.id}/fundraisers/{self.fundraiser.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_owner_can_access_own_fundraiser(self):
        """
        User A can read their own fundraiser — happy path must still work.
        """
        self.client.force_authenticate(user=self.user_a)
        url = f'/api/v1/organizations/{self.org_a.id}/fundraisers/{self.fundraiser.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ContributionTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.admin_user = User.objects.create_user(
            username='contrib_admin', password='pass123'
        )
        self.member_user = User.objects.create_user(
            username='contrib_member', password='pass123'
        )
        Membership.objects.create(
            user=self.admin_user, organization=self.org, role='admin'
        )
        Membership.objects.create(
            user=self.member_user, organization=self.org, role='member'
        )
        self.fundraiser = Fundraiser.objects.create(
            organization=self.org,
            title="Test Fundraiser",
            description="For testing",
            goal_amount=50000,
            status='draft'
        )
        self.client = APIClient()
        self.url = f'/api/v1/organizations/{self.org.id}/fundraisers/{self.fundraiser.id}/contributions/'

    def test_member_can_create_contribution(self):
        """Any org member can record a contribution."""
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(self.url, {
            'fundraiser': self.fundraiser.id,
            'amount': '500.00',
            'payment_method': 'manual'
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_contribution_amount_must_be_positive(self):
        """Zero or negative amounts must be rejected."""
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(self.url, {
            'fundraiser': self.fundraiser.id,
            'amount': '0.00',
            'payment_method': 'manual'
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_member_sees_only_own_contributions(self):
        """A member listing contributions sees only their own."""
        # Admin contributes
        Contribution.objects.create(
            organization=self.org,
            fundraiser=self.fundraiser,
            contributor=self.admin_user,
            amount=1000,
            payment_method='manual'
        )
        # Member contributes
        Contribution.objects.create(
            organization=self.org,
            fundraiser=self.fundraiser,
            contributor=self.member_user,
            amount=500,
            payment_method='manual'
        )
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Member must only see their own single contribution
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '500.00')

    def test_admin_sees_all_contributions(self):
        """An admin listing contributions sees everyone's."""
        Contribution.objects.create(
            organization=self.org,
            fundraiser=self.fundraiser,
            contributor=self.admin_user,
            amount=1000,
            payment_method='manual'
        )
        Contribution.objects.create(
            organization=self.org,
            fundraiser=self.fundraiser,
            contributor=self.member_user,
            amount=500,
            payment_method='manual'
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_access_contributions(self):
        """No JWT, no access."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_fundraiser_injection_in_body_is_ignored(self):
        """
        Attacker sends a foreign org's fundraiser ID in the POST body.
        The view must ignore it and bind to the fundraiser from the URL.
        The contribution must land on the correct fundraiser, not the injected one.
        """
        # Create a foreign org and fundraiser the authenticated user has no access to
        foreign_org = Organization.objects.create(name="Foreign Org")
        foreign_fundraiser = Fundraiser._base_manager.create(
            organization=foreign_org,
            title="Foreign Fundraiser",
            goal_amount=99999,
            status='published',
        )

        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(self.url, {
            'amount': '500.00',
            'payment_method': 'manual',
            'fundraiser': foreign_fundraiser.id,  # injected — must be silently ignored
        }, format='json')

        self.assertEqual(response.status_code, 201)

        # The contribution must be bound to the URL's fundraiser, not the injected one
        created = Contribution.objects.filter(contributor=self.member_user).latest('id')
        self.assertEqual(created.fundraiser, self.fundraiser)
        self.assertNotEqual(created.fundraiser, foreign_fundraiser)

    def test_non_member_cannot_post_contribution(self):
        """
        A valid authenticated user who is NOT a member of this org
        must be refused at the contributions endpoint.
        Expected: 404 — we never confirm the resource exists to outsiders.
        """
        outsider = User.objects.create_user(
            username='outsider', password='pass123'
        )

        self.client.force_authenticate(user=outsider)
        response = self.client.post(self.url, {
            'amount': '500.00',
            'payment_method': 'manual',
        }, format='json')

        self.assertEqual(response.status_code, 404)

    def test_non_member_cannot_list_contributions(self):
        """
        Same outsider, hitting GET instead of POST.
        Must also return 404 — list and create share the same tenancy gate.
        """
        outsider = User.objects.create_user(
            username='outsider_list', password='pass123'
        )

        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
