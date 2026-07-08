from rest_framework_simplejwt.views import TokenObtainPairView
from core.throttles import LoginRateThrottle
from core.models import Membership
from django.contrib.auth import get_user_model

User = get_user_model()


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # request.user is AnonymousUser here — look up by username instead
            user = User.objects.get(username=request.data['username'])

            memberships = Membership.objects.filter(
                user=user
            ).select_related('organization')

            response.data['organizations'] = [
                {
                    'id': m.organization.id,
                    'name': m.organization.name,
                    'role': m.role,
                }
                for m in memberships
            ]

        return response
