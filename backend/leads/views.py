from django.shortcuts import render
from rest_framework import generics
from .models import Lead
from .serializers import LeadSerializer

class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    throttle_classes = [AnonRateThrottle]
