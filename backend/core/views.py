from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from core.throttles import LoginRateThrottle
from core.models import Membership
from django.contrib.auth import get_user_model

User = get_user_model()

REFRESH_COOKIE_NAME = 'refresh_token'
COOKIE_SETTINGS = {
    'httponly': True,       # JS cannot read this — closes XSS theft vector
    'secure': False,        # Set True in production (requires HTTPS)
    'samesite': 'Strict',   # Browser won't send cookie on cross-origin requests — closes CSRF vector
    'max_age': 7 * 24 * 60 * 60,  # 7 days, matches SIMPLE_JWT REFRESH_TOKEN_LIFETIME
    'path': '/api/v1/auth/token/refresh/',  # Cookie only sent to the refresh endpoint — minimises exposure
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
