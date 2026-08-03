from django.urls import path
from .views import (
    FundraiserListCreateView,
    FundraiserDetailView,
    ContributionListCreateView,
    PublishFundraiserView,
    CloseFundraiserView,
    BeneficiaryListCreateView,
    FundraiserBeneficiaryListCreateView,
)

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
    path(
        "organizations/<int:org_id>/fundraisers/<int:fundraiser_id>/publish/",
        PublishFundraiserView.as_view(),
        name="fundraiser-publish",
    ),
    path(
        "organizations/<int:org_id>/fundraisers/<int:fundraiser_id>/close/",
        CloseFundraiserView.as_view(),
        name="fundraiser-close",
    ),
    path(
        "organizations/<int:org_id>/fundraisers/<int:fundraiser_id>/contributions/",
        ContributionListCreateView.as_view(),
        name="contribution-list-create",
    ),
    path(
        'organizations/<int:org_id>/beneficiaries/',
        BeneficiaryListCreateView.as_view(),
        name='beneficiary-list-create'
    ),
    path(
        "organizations/<int:org_id>/fundraisers/<int:fundraiser_pk>/beneficiaries/",
        FundraiserBeneficiaryListCreateView.as_view(),
        name="fundraiser-beneficiary-list",
    ),

]
