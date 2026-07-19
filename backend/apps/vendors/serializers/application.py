from django.db import transaction
from rest_framework import serializers

from apps.users.models import User
from apps.vendors.models import VendorProfile
from apps.vendors.utils import generate_unique_store_slug


class VendorApplicationSerializer(serializers.ModelSerializer):
    """Handles POST /api/vendors/apply/. Turns a customer into a vendor
    in one step: flips User.role to "vendor" and creates the
    VendorProfile (status="pending") together inside a transaction, so
    the two can never end up out of sync with each other."""

    class Meta:
        model = VendorProfile
        fields = ["id", "store_name", "description", "logo_url", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        if hasattr(user, "vendor_profile"):
            raise serializers.ValidationError("You already have a vendor profile.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            profile = VendorProfile.objects.create(
                user=user,
                store_slug=generate_unique_store_slug(validated_data["store_name"]),
                **validated_data,
            )
            user.role = User.Role.VENDOR
            user.save(update_fields=["role"])
        return profile
