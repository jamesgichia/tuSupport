# fundraisers/urls.py

from django.urls import path
from .views import FundraiserListCreateView

urlpatterns = [
    path(
        "organizations/<int:org_id>/fundraisers/",   # org_id captured from the URL itself
        FundraiserListCreateView.as_view(),
        name="fundraiser-list-create",
    ),
    # Old flat route is REMOVED — no more "unlocked door" left standing
]
