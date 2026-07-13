from django.urls import path
from core.views import MembershipUpdateView

urlpatterns = [
    path(
        'organizations/<int:org_id>/memberships/<int:membership_id>/',
        MembershipUpdateView.as_view(),
        name='membership-update'
    ),
]
