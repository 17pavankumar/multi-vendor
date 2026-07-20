from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    """Just validates the checkout request's shape — apps.orders.services.
    checkout() does the actual work and raises CheckoutError for
    anything this can't express (empty cart, insufficient stock, a
    coupon that doesn't apply)."""

    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
