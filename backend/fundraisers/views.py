from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
from .models import Fundraiser, Contribution
from .serializers import FundraiserSerializer, ContributionSerializer
from core.models import Membership


class FundraiserListCreateView(generics.ListCreateAPIView):
    serializer_class = FundraiserSerializer

    def get_membership_or_404(self):
        """
        Single source of truth for the org check.
        Reads org_id from the URL, verifies the user
        actually belongs to it. Returns membership or
        raises 404 — never 403 (don't confirm org exists).
        """
        org_id = self.kwargs["org_id"]  # declared intent from URL
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if membership is None:
            raise Http404  # attacker learns nothing
        return membership

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Fundraiser._base_manager.none()
        membership = self.get_membership_or_404()  # verified, not assumed
        return Fundraiser.objects.for_org(
            membership.organization
        ).filter(status='published')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = self.get_membership_or_404()

        # Role check — members can read, only admins can write
        if membership.role != Membership.Role.ADMIN:
            raise PermissionDenied("Only organisation admins can create fundraisers.")

        instance = Fundraiser(
            organization=membership.organization,
            status='draft',
            **serializer.validated_data
        )
        instance.save()

        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class FundraiserDetailView(generics.RetrieveAPIView):
    """
    GET a single fundraiser by ID.
    Tenant check happens first — if the requesting user doesn't belong
    to the org in the URL, they get 404. Never 403.
    If they do belong but the fundraiser belongs to a different org,
    they also get 404 — the fundraiser is invisible to them.
    """
    serializer_class = FundraiserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Step 1 — verify requester belongs to the org declared in the URL
        org_id = self.kwargs['org_id']
        membership = self.request.user.membership_set.filter(
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404  # user doesn't belong here — reveal nothing

        # Step 2 — fetch the fundraiser, scoped to this org
        # If the fundraiser exists but belongs to a different org, this returns None → 404
        fundraiser = Fundraiser.objects.filter(
            id=self.kwargs['fundraiser_id'],
            organization_id=org_id       # tenant scope enforced here
        ).first()
        if not fundraiser:
            raise Http404

        return fundraiser


class ContributionListCreateView(generics.ListCreateAPIView):
    """
    GET  — list contributions for a fundraiser (tenant-scoped)
    POST — record a new contribution (any authenticated org member)
    
    Admin sees all contributions for the fundraiser.
    Member sees only their own contributions.
    """
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def get_membership_or_404(self):
        """Reuse the same tenant enforcement pattern as FundraiserListCreateView."""
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

        # Verify fundraiser belongs to this org before listing contributions
        fundraiser = Fundraiser.objects.filter(
            id=fundraiser_id,
            organization=membership.organization
        ).first()
        if not fundraiser:
            raise Http404

        qs = Contribution.objects.filter(fundraiser=fundraiser)

        # Admins see all contributions; members see only their own
        if membership.role != Membership.Role.ADMIN:
            qs = qs.filter(contributor=self.request.user)

        return qs

    def get_serializer_context(self):
        """Pass org_id into serializer so validate_fundraiser can use it."""
        context = super().get_serializer_context()
        context['org_id'] = self.kwargs['org_id']
        return context

    def perform_create(self, serializer):
        membership = self.get_membership_or_404()
        serializer.save(
            contributor=self.request.user,
            organization=membership.organization
        )
