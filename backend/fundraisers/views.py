from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Fundraiser
from .serializers import FundraiserSerializer


class FundraiserListCreateView(generics.ListCreateAPIView):
    serializer_class = FundraiserSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Fundraiser._base_manager.none()
        membership = self.request.user.membership_set.first()
        if membership is None:
            return Fundraiser._base_manager.none()
        return Fundraiser.objects.for_org(membership.organization).filter(status='published')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = request.user.membership_set.first()
        if membership is None:
            raise PermissionDenied("You must belong to an organization to create a fundraiser.")

        instance = Fundraiser(
            organization=membership.organization,
            status='draft',
            **serializer.validated_data
        )
        instance.save()

        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
