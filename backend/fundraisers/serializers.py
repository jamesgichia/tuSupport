from rest_framework import serializers
from .models import Fundraiser

class FundraiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fundraiser
        fields = ['id', 'title', 'description', 'goal_amount', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
