from rest_framework import serializers
from .models import Fundraiser, Contribution
from decimal import Decimal

class FundraiserSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        min_length=5,
        max_length=255,
        trim_whitespace=True
    )
    description = serializers.CharField(
        max_length=5000,
        allow_blank=True,
        required=False
    )
    goal_amount = serializers.DecimalField(
        max_digits=12,          # matches the model exactly
        decimal_places=2,
        min_value=Decimal('1.00'),
        max_value=Decimal('10000000.00')
    )

    class Meta:
        model = Fundraiser
        fields = ['id', 'title', 'description', 'goal_amount', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']



class ContributionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        max_value=Decimal('999999.99')
    )
    payment_method = serializers.ChoiceField(
        choices=Contribution.PaymentMethod.choices
    )
    phone_number = serializers.CharField(
        max_length=15,
        allow_null=True,
        required=False
    )
    notes = serializers.CharField(
        max_length=2000,
        allow_blank=True,
        required=False
    )
    contributor_name = serializers.CharField(
        max_length=100,
        allow_blank=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Contribution
        fields = [
            'id', 'fundraiser', 'contributor', 'contributor_name',
            'amount', 'payment_method', 'phone_number', 'transaction_id',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'contributor', 'fundraiser', 'created_at', 'transaction_id']

    def validate(self, data):
        if data.get('payment_method') == 'mpesa' and not data.get('phone_number'):
            raise serializers.ValidationError(
                {"phone_number": "Phone number is required for M-Pesa payments."}
            )
        return data
