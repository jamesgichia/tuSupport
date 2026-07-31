from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from core.throttles import LoginRateThrottle
from core.models import Membership
from django.contrib.auth import get_user_model
from core.serializers import MembershipSerializer


User = get_user_model()

REFRESH_COOKIE_NAME = 'refresh_token'
COOKIE_SETTINGS = {
    'httponly': True,       # JS cannot read this — closes XSS theft vector
    'secure': False,        # Set True in production (requires HTTPS)
    'samesite': 'Strict',   # Browser won't send cookie on cross-origin requests — closes CSRF vector
    'max_age': 7 * 24 * 60 * 60,  # 7 days, matches SIMPLE_JWT REFRESH_TOKEN_LIFETIME
    'path': '/api/v1/auth/',  # only send cookie to auth endpoints
}


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    Login view. Returns access token in JSON, refresh token as HttpOnly cookie.
    The refresh token never touches the frontend JS environment.
    """
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Pull refresh token out of JSON before it reaches the frontend
            refresh_token = response.data.pop('refresh')

            # Set it as an HttpOnly cookie instead
            response.set_cookie(REFRESH_COOKIE_NAME, refresh_token, **COOKIE_SETTINGS)

            # Attach org list to JSON response
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


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh view. Reads refresh token from HttpOnly cookie, not request body.
    The frontend sends an empty POST — the browser attaches the cookie automatically.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token missing.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Inject the cookie value into request data so the parent view can process it normally
        request.data['refresh'] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)
        except (TokenError, InvalidToken) as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == 200:
            # ROTATE_REFRESH_TOKENS=True means a new refresh token was issued — update the cookie
            new_refresh = response.data.pop('refresh', None)
            if new_refresh:
                response.set_cookie(REFRESH_COOKIE_NAME, new_refresh, **COOKIE_SETTINGS)

        return response



class MembershipUpdateView(generics.UpdateAPIView):
    """
    PATCH only — allows role changes by admins.
    Members attempting to escalate their own role are rejected
    at the serializer level (validate_role).
    """
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']  # explicitly block PUT — partial updates only

    def get_object(self):
        org_id = self.kwargs['org_id']
        membership_id = self.kwargs['membership_id']

        # First verify the requester belongs to this org
        # 404 not 403 — don't confirm the org exists to outsiders
        requester_membership = Membership.objects.filter(
            user=self.request.user,
            organization_id=org_id
        ).first()
        if not requester_membership:
            raise Http404

        # Then fetch the target membership
        membership = Membership.objects.filter(
            id=membership_id,
            organization_id=org_id
        ).first()
        if not membership:
            raise Http404

        return membership

    def get_serializer_context(self):
        # Pass org_id into serializer so validate_role can use it
        context = super().get_serializer_context()
        context['org_id'] = self.kwargs['org_id']
        return context



class LogoutView(APIView):
    """
    Logout view. Reads refresh token from HttpOnly cookie,
    blacklists it, then clears the cookie from the browser.
    No request body needed — browser sends cookie automatically.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response(
                {'detail': 'No active session found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # writes to simplejwt blacklist table
        except (TokenError, InvalidToken):
            # Token already expired or invalid — still clear the cookie
            pass

        response = Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )

        # Clear the cookie from the browser
        response.delete_cookie(
            REFRESH_COOKIE_NAME,
            path='/api/v1/auth/',      # must match the path the cookie was set with
            samesite='Strict',
        )

        return response
