from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from core.throttles import LoginRateThrottle

class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]
