from rest_framework import serializers
from core.models import Membership


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['id', 'user', 'organization', 'role', 'created_at']
        read_only_fields = ['user', 'organization', 'created_at']

    def validate_role(self, value):
        """
        Only an org admin may write the role field.
        Protection lives here — travels with the serializer,
        not with any single view.
        """
        request = self.context.get('request')
        org_id = self.context.get('org_id')

        is_admin = Membership.objects.filter(
            user=request.user,
            organization_id=org_id,
            role=Membership.Role.ADMIN
        ).exists()

        if not is_admin:
            raise serializers.ValidationError(
                "Only organisation admins can change membership roles."
            )
        return value
