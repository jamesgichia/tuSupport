from django.urls import path
from .views import FundraiserListCreateView, FundraiserDetailView

urlpatterns = [
    path(
        "organizations/<int:org_id>/fundraisers/",
        FundraiserListCreateView.as_view(),
        name="fundraiser-list-create",
    ),
    path(
        "organizations/<int:org_id>/fundraisers/<int:fundraiser_id>/",
        FundraiserDetailView.as_view(),
        name="fundraiser-detail",
    ),
]
