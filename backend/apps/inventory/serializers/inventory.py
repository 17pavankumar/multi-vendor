from rest_framework import serializers

from apps.inventory.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    """GET/PATCH on the logged-in vendor's own stock levels.
    reserved_quantity is read-only here on purpose — it's meant to move
    automatically as orders are placed/cancelled (Phase 5's checkout
    flow), not something a vendor edits by hand. `quantity` (restocking)
    and `low_stock_threshold` are the two fields a vendor actually
    manages themselves."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id", "product", "product_name", "quantity", "reserved_quantity",
            "low_stock_threshold", "available_quantity", "is_low_stock", "updated_at",
        ]
        read_only_fields = ["id", "product", "reserved_quantity", "updated_at"]
