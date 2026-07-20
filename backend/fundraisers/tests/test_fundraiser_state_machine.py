from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Organization, Membership
from fundraisers.models import Fundraiser

User = get_user_model()


class FundraiserStateMachineTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create org + admin user
        self.org = Organization.objects.create(name="Test Org")
        self.admin = User.objects.create_user(
            username="admin", password="pass", email="admin@test.com"
        )
        Membership.objects.create(
            user=self.admin, organization=self.org, role=Membership.Role.ADMIN
        )

        # Create a plain member
        self.member = User.objects.create_user(
            username="member", password="pass", email="member@test.com"
        )
        Membership.objects.create(
            user=self.member, organization=self.org, role=Membership.Role.MEMBER
        )

        # A draft fundraiser to work with
        self.fundraiser = Fundraiser.objects.create(
            organization=self.org,
            title="Test Fundraiser",
            goal_amount="10000.00",
            status=Fundraiser.Status.DRAFT,
        )

        self.publish_url = (
            f"/api/v1/organizations/{self.org.id}"
            f"/fundraisers/{self.fundraiser.id}/publish/"
        )
        self.close_url = (
            f"/api/v1/organizations/{self.org.id}"
            f"/fundraisers/{self.fundraiser.id}/close/"
        )
        self.contribution_url = (
            f"/api/v1/organizations/{self.org.id}"
            f"/fundraisers/{self.fundraiser.id}/contributions/"
        )

    # --- Publish transition ---

    def test_admin_can_publish_draft(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.publish_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fundraiser.refresh_from_db()
        self.assertEqual(self.fundraiser.status, Fundraiser.Status.PUBLISHED)

    def test_member_cannot_publish(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.publish_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_publish_already_published(self):
        self.fundraiser.status = Fundraiser.Status.PUBLISHED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.publish_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_publish_closed_fundraiser(self):
        self.fundraiser.status = Fundraiser.Status.CLOSED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.publish_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Close transition ---

    def test_admin_can_close_published(self):
        self.fundraiser.status = Fundraiser.Status.PUBLISHED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.close_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fundraiser.refresh_from_db()
        self.assertEqual(self.fundraiser.status, Fundraiser.Status.CLOSED)

    def test_cannot_close_draft(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.close_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_close_already_closed(self):
        self.fundraiser.status = Fundraiser.Status.CLOSED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.close_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Contribution guard ---

    def test_cannot_contribute_to_draft_fundraiser(self):
        # fundraiser is still draft from setUp
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.contribution_url, {
            "amount": "500.00",
            "payment_method": "manual",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_contribute_to_closed_fundraiser(self):
        self.fundraiser.status = Fundraiser.Status.CLOSED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.contribution_url, {
            "amount": "500.00",
            "payment_method": "manual",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_contribute_to_published_fundraiser(self):
        self.fundraiser.status = Fundraiser.Status.PUBLISHED
        self.fundraiser.save()
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.contribution_url, {
            "amount": "500.00",
            "payment_method": "manual",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
