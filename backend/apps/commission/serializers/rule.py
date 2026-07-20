from rest_framework import serializers

from apps.commission.models import CommissionRule


class CommissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRule
        fields = ["id", "vendor", "category", "rate", "created_at"]
        read_only_fields = ["id", "created_at"]
