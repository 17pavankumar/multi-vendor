from rest_framework import serializers

from apps.products.selectors import visible_products
from apps.wishlist.models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.effective_price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_name", "product_price", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_product(self, product):
        if not visible_products().filter(pk=product.pk).exists():
            raise serializers.ValidationError("This product isn't available.")
        return product

    def validate(self, attrs):
        user = self.context["request"].user
        if WishlistItem.objects.filter(user=user, product=attrs["product"]).exists():
            raise serializers.ValidationError("This product is already on your wishlist.")
        return attrs

    def create(self, validated_data):
        return WishlistItem.objects.create(user=self.context["request"].user, **validated_data)
