from rest_framework import serializers
from .models import Fundraiser, Contribution

class FundraiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fundraiser
        fields = ['id', 'title', 'description', 'goal_amount', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = [
            'id', 'fundraiser', 'contributor', 'amount',
            'payment_method', 'phone_number', 'transaction_id',
            'notes', 'created_at'
        ]
        # fundraiser now injected by the view from the URL — client cannot declare it
        read_only_fields = ['id', 'contributor', 'fundraiser', 'created_at', 'transaction_id']

    def validate_amount(self, value):
        """Amount must be positive — a zero or negative contribution is nonsensical."""
        if value <= 0:
            raise serializers.ValidationError("Contribution amount must be greater than zero.")
        return value
