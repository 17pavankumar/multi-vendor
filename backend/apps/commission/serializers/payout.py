from rest_framework import serializers

from apps.commission.models import VendorPayout


class VendorPayoutSerializer(serializers.ModelSerializer):
    """Read-only — payouts are only ever created by
    tasks.generate_vendor_payouts, never edited directly; the one state
    change available (marking one paid) goes through a dedicated action
    endpoint instead of a PATCH on this serializer, so "paid_at" can
    never be set to an arbitrary value."""

    vendor_store_name = serializers.CharField(source="vendor.store_name", read_only=True)

    class Meta:
        model = VendorPayout
        fields = [
            "id", "vendor", "vendor_store_name", "period_start", "period_end",
            "gross_amount", "commission_amount", "net_amount", "status", "paid_at", "created_at",
        ]


class GeneratePayoutsSerializer(serializers.Serializer):
    period_start = serializers.DateField()
    period_end = serializers.DateField()

    def validate(self, attrs):
        if attrs["period_end"] < attrs["period_start"]:
            raise serializers.ValidationError("period_end must be on or after period_start.")
        return attrs
