from django.urls import path
from core.views import MembershipUpdateView, LogoutView

urlpatterns = [
    path(
        'organizations/<int:org_id>/memberships/<int:membership_id>/',
        MembershipUpdateView.as_view(),
        name='membership-update'
    ),
    path(
        'auth/logout/',
        LogoutView.as_view(),
        name='auth-logout'
    ),
]
