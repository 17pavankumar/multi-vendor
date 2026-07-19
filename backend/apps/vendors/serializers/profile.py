from rest_framework import serializers

from apps.vendors.models import VendorProfile


class VendorProfileSerializer(serializers.ModelSerializer):
    """GET/PATCH on the logged-in vendor's own profile. store_slug and
    the approval fields are read-only here — the slug is fixed once set
    (product URLs may already reference it), and approval status only
    changes through the admin approval flow, never a self-edit."""

    class Meta:
        model = VendorProfile
        fields = [
            "id", "store_name", "store_slug", "description", "logo_url",
            "status", "default_commission_rate", "approved_at", "created_at",
        ]
        read_only_fields = [
            "id", "store_slug", "status", "default_commission_rate", "approved_at", "created_at",
        ]
