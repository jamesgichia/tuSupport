from rest_framework import serializers
from .models import Fundraiser, Contribution, Beneficiary, FundraiserBeneficiary
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
        # Existing M-Pesa check
        if data.get('payment_method') == 'mpesa' and not data.get('phone_number'):
            raise serializers.ValidationError(
                {"phone_number": "Phone number is required for M-Pesa payments."}
            )

        # NULL/NULL guard — a contribution must have at least one identity signal
        if not data.get('contributor_name') and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError(
                {"non_field_errors": ["A contribution must have either a linked account or a contributor name."]}
            )

        return data



class BeneficiaryPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            'id', 'display_name', 'category',
            'verification_status', 'created_at'
        ]
        read_only_fields = ['id', 'verification_status', 'created_at']


class BeneficiaryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            'id', 'display_name', 'category', 'verification_status',
            'full_name', 'national_id', 'phone_number',
            'relationship_to_org', 'internal_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FundraiserBeneficiarySerializer(serializers.ModelSerializer):
    # Read-only nested detail — so the API consumer sees names, not just IDs
    beneficiary_name = serializers.CharField(
        source="beneficiary.full_name", read_only=True
    )

    class Meta:
        model = FundraiserBeneficiary
        fields = [
            "id",
            "beneficiary",        # write: accepts beneficiary ID on POST
            "beneficiary_name",   # read: returns human-readable name
            "notes",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by", "beneficiary_name"]
