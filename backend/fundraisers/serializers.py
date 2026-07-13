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
        # Server sets these — never trust the client to declare who contributed
        read_only_fields = ['id', 'contributor', 'created_at', 'transaction_id']

    def validate_amount(self, value):
        """Amount must be positive — a zero or negative contribution is nonsensical."""
        if value <= 0:
            raise serializers.ValidationError("Contribution amount must be greater than zero.")
        return value

    def validate_fundraiser(self, value):
        """
        Fundraiser must belong to the same org declared in the URL.
        Prevents a member of Org A submitting a contribution
        that points at Org B's fundraiser.
        """
        org_id = self.context.get('org_id')
        if str(value.organization_id) != str(org_id):
            raise serializers.ValidationError(
                "Fundraiser does not belong to this organisation."
            )
        return value
