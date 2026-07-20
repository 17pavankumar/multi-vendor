from rest_framework import serializers

from apps.cart.models import CartItem
from apps.products.selectors import visible_products


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "line_total", "created_at"]
        read_only_fields = ["id", "unit_price", "created_at"]

    def validate_product(self, product):
        if not visible_products().filter(pk=product.pk).exists():
            raise serializers.ValidationError("This product isn't available for purchase.")
        return product

    def create(self, validated_data):
        cart = self.context["cart"]
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        # Adding a product already in the cart increases the existing
        # line's quantity instead of erroring — matches the intent
        # behind the UNIQUE (cart, product) constraint (at most one row
        # per product per cart).
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "unit_price": product.effective_price},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        return item
