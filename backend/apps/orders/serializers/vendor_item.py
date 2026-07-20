from rest_framework import serializers

from apps.orders.models import OrderItem


class VendorOrderItemSerializer(serializers.ModelSerializer):
    """A vendor's view of one of their sales. Everything is read-only
    except `fulfillment_status` — that's the one thing a vendor
    actually manages here (pending -> packed -> shipped -> delivered);
    full shipment tracking with carrier/tracking numbers is a later
    phase (db/schema.sql's shipments table)."""

    order_number = serializers.UUIDField(source="order.order_number", read_only=True)
    order_status = serializers.CharField(source="order.status", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    customer_email = serializers.EmailField(source="order.user.email", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "order_number", "order_status", "product", "product_name", "customer_email",
            "quantity", "unit_price", "subtotal", "commission_amount", "fulfillment_status",
        ]
        read_only_fields = [
            "id", "order_number", "order_status", "product", "product_name",
            "customer_email", "quantity", "unit_price", "subtotal", "commission_amount",
        ]
