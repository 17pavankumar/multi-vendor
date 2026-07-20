from rest_framework import serializers

from apps.cart.models import Cart
from apps.cart.serializers.item import CartItemSerializer


class CartSerializer(serializers.ModelSerializer):
    """Read-only summary of the whole cart — GET /api/cart/. `subtotal`
    reads straight from the Cart.subtotal model property rather than
    recomputing it here, so there's one definition of "how a cart
    total is calculated"."""

    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "updated_at"]
