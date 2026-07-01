# fundraisers/urls.py
from django.urls import path
from .views import FundraiserListCreateView

urlpatterns = [
    path('fundraisers/', FundraiserListCreateView.as_view(), name='fundraiser-list-create'),
]
