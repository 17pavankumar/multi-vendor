from rest_framework import serializers

from apps.vendors.models import VendorProfile


class VendorAdminListSerializer(serializers.ModelSerializer):
    """Read-only view used by admins to review vendor applications and
    to confirm the result of an approve/reject action."""

    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            "id", "store_name", "store_slug", "email", "status",
            "default_commission_rate", "approved_at", "created_at",
        ]
