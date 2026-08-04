from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Fundraiser, Contribution, Beneficiary, FundraiserBeneficiary
from .serializers import FundraiserReadSerializer, FundraiserSerializer, ContributionSerializer, FundraiserBeneficiarySerializer, BeneficiaryAdminSerializer, BeneficiaryPublicSerializer
from .serializers import BeneficiaryAdminSerializer, BeneficiaryPublicSerializer, FundraiserBeneficiarySerializer
from core.models import Membership


class FundraiserListCreateView(generics.ListCreateAPIView):
    serializer_class = FundraiserSerializer

    def get_membership_or_404(self):
        org_id = self.kwargs["org_id"]
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if membership is None:
            raise Http404
        return membership

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Fundraiser._base_manager.none()
        membership = self.get_membership_or_404()
        qs = Fundraiser.objects.for_org(membership.organization)

        # Admins see everything (draft, published, closed)
        # Members only see published fundraisers
        if membership.role != Membership.Role.ADMIN:
            qs = qs.filter(status=Fundraiser.Status.PUBLISHED)

        return qs

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = self.get_membership_or_404()

        if membership.role != Membership.Role.ADMIN:
            raise PermissionDenied("Only organisation admins can create fundraisers.")

        instance = Fundraiser(
            organization=membership.organization,
            status=Fundraiser.Status.DRAFT,
            **serializer.validated_data
        )
        instance.save()

        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class FundraiserDetailView(generics.RetrieveAPIView):
    serializer_class = FundraiserReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        org_id = self.kwargs['org_id']
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404

        fundraiser = Fundraiser.objects.filter(
            id=self.kwargs['fundraiser_id'],
            organization_id=org_id
        ).first()
        if not fundraiser:
            raise Http404

        return fundraiser


class PublishFundraiserView(APIView):
    """
    POST /organizations/<org_id>/fundraisers/<fundraiser_id>/publish/
    Admin-only. Moves a fundraiser from draft → published.
    Rejects any other starting state.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id, fundraiser_id):
        # Step 1 — verify membership and admin role
        membership = request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404
        if membership.role != Membership.Role.ADMIN:
            raise PermissionDenied("Only admins can publish fundraisers.")

        # Step 2 — fetch fundraiser scoped to this org
        fundraiser = Fundraiser.objects.filter(
            id=fundraiser_id,
            organization=membership.organization
        ).first()
        if not fundraiser:
            raise Http404

        # Step 3 — enforce valid transition: only draft → published is allowed
        if fundraiser.status != Fundraiser.Status.DRAFT:
            raise ValidationError(
                f"Cannot publish a fundraiser with status '{fundraiser.status}'. "
                "Only draft fundraisers can be published."
            )

        fundraiser.status = Fundraiser.Status.PUBLISHED
        fundraiser.save()

        return Response(
            FundraiserSerializer(fundraiser).data,
            status=status.HTTP_200_OK
        )


class CloseFundraiserView(APIView):
    """
    POST /organizations/<org_id>/fundraisers/<fundraiser_id>/close/
    Admin-only. Moves a fundraiser from published → closed.
    Closed is a terminal state — it cannot be undone.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id, fundraiser_id):
        membership = request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404
        if membership.role != Membership.Role.ADMIN:
            raise PermissionDenied("Only admins can close fundraisers.")

        fundraiser = Fundraiser.objects.filter(
            id=fundraiser_id,
            organization=membership.organization
        ).first()
        if not fundraiser:
            raise Http404

        # Only published fundraisers can be closed
        # A draft that was never live cannot be "closed" — it should just be deleted
        if fundraiser.status != Fundraiser.Status.PUBLISHED:
            raise ValidationError(
                f"Cannot close a fundraiser with status '{fundraiser.status}'. "
                "Only published fundraisers can be closed."
            )

        fundraiser.status = Fundraiser.Status.CLOSED
        fundraiser.save()

        return Response(
            FundraiserSerializer(fundraiser).data,
            status=status.HTTP_200_OK
        )


class ContributionListCreateView(generics.ListCreateAPIView):
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def get_membership_or_404(self):
        org_id = self.kwargs['org_id']
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404
        return membership

    def get_queryset(self):
        membership = self.get_membership_or_404()
        fundraiser_id = self.kwargs['fundraiser_id']

        fundraiser = Fundraiser.objects.filter(
            id=fundraiser_id,
            organization=membership.organization
        ).first()
        if not fundraiser:
            raise Http404

        qs = Contribution.objects.filter(fundraiser=fundraiser)

        if membership.role != Membership.Role.ADMIN:
            qs = qs.filter(contributor=self.request.user)

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['org_id'] = self.kwargs['org_id']
        return context

    def perform_create(self, serializer):
        membership = self.get_membership_or_404()

        fundraiser = Fundraiser.objects.filter(
            id=self.kwargs['fundraiser_id'],
            organization=membership.organization
        ).first()
        if not fundraiser:
            raise Http404

        # State machine guard — only published fundraisers accept contributions
        if fundraiser.status != Fundraiser.Status.PUBLISHED:
            raise ValidationError(
                f"This fundraiser is not accepting contributions "
                f"(current status: '{fundraiser.status}')."
            )

        user = self.request.user

        # Step 2: Resolve contributor_name based on role
        if membership.role == Membership.Role.ADMIN:
            # Admins may record on behalf of a third party
            # If they supply a name, use it; otherwise fall back to their own account name
            contributor_name = (
                serializer.validated_data.get('contributor_name')
                or f"{user.first_name} {user.last_name}".strip()
                or user.username
            )
        else:
            # Regular members — derive strictly from account, ignore client input
            contributor_name = (
                f"{user.first_name} {user.last_name}".strip()
                or user.username
            )

        serializer.save(
            contributor=user,
            organization=membership.organization,
            fundraiser=fundraiser,
            contributor_name=contributor_name
        )


class BeneficiaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_membership_or_404(self):
        org_id = self.kwargs['org_id']
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404
        return membership

    def get_serializer_class(self):
        membership = self.get_membership_or_404()
        if membership.role == Membership.Role.ADMIN:
            return BeneficiaryAdminSerializer
        return BeneficiaryPublicSerializer

    def get_queryset(self):
        membership = self.get_membership_or_404()
        return Beneficiary.objects.filter(
            organization=membership.organization
        )

    def perform_create(self, serializer):
        membership = self.get_membership_or_404()
        # Only admins may create beneficiary records
        if membership.role != Membership.Role.ADMIN:
            raise PermissionDenied(
                "Only administrators can register beneficiaries."
            )
        serializer.save(organization=membership.organization)



class FundraiserBeneficiaryListCreateView(generics.ListCreateAPIView):
    serializer_class = FundraiserBeneficiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs["org_id"]
        # Verify the requesting user is a member of this organization
        membership = get_object_or_404(
            self.request.user.membership_set,
            organization_id=org_id,
        )
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=self.kwargs["fundraiser_pk"],
            organization=membership.organization,  # tenant check
        )
        return FundraiserBeneficiary.objects.filter(fundraiser=fundraiser)

    def perform_create(self, serializer):
        org_id = self.kwargs["org_id"]
        membership = get_object_or_404(
            self.request.user.membership_set,
            organization_id=org_id,
        )
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=self.kwargs["fundraiser_pk"],
            organization=membership.organization,  # tenant check
        )
        beneficiary = get_object_or_404(
            Beneficiary,
            pk=serializer.validated_data["beneficiary"].pk,
            organization=membership.organization,  # tenant check — IDOR closed
        )
        serializer.save(
            fundraiser=fundraiser,
            beneficiary=beneficiary,
            organization=membership.organization,
            created_by=self.request.user,
        )
