from rest_framework import serializers

from apps.coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """Create/update a coupon. `vendor` is never client-writable — the
    view supplies it: the caller's own VendorProfile for a vendor-scoped
    coupon (views/vendor.py), or None for an admin-created platform-wide
    one (views/admin.py)."""

    class Meta:
        model = Coupon
        fields = [
            "id", "code", "discount_type", "discount_value", "min_order_amount",
            "max_discount_amount", "usage_limit", "usage_count", "valid_from",
            "valid_until", "is_active", "created_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at"]

    def validate(self, attrs):
        # The model has a matching DB-level CheckConstraint
        # (chk_coupon_dates), but DRF doesn't run Django's model
        # validation/constraints before INSERT — without this check, a
        # bad date range would surface as a raw IntegrityError (500)
        # instead of a normal 400 response.
        valid_from = attrs.get("valid_from", getattr(self.instance, "valid_from", None))
        valid_until = attrs.get("valid_until", getattr(self.instance, "valid_until", None))
        if valid_from and valid_until and valid_until <= valid_from:
            raise serializers.ValidationError("valid_until must be after valid_from.")
        return attrs
