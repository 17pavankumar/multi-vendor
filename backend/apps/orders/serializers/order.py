from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    vendor_store_name = serializers.CharField(source="vendor.store_name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_name", "vendor_store_name", "quantity",
            "unit_price", "subtotal", "fulfillment_status",
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Read-only — an order and its items are created exclusively
    through checkout (services.checkout), never edited via this
    serializer."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "subtotal", "discount_amount",
            "shipping_amount", "tax_amount", "total_amount", "items", "placed_at",
        ]
