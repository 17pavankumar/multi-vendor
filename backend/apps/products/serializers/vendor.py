from django.utils.text import slugify
from rest_framework import serializers

from apps.products.models import Product


class VendorProductSerializer(serializers.ModelSerializer):
    """Create/update on the logged-in vendor's own catalog. `vendor` is
    deliberately not a field here — the view always supplies it as the
    caller's own VendorProfile via serializer.save(vendor=...), so
    there's no way to create a product under someone else's store."""

    class Meta:
        model = Product
        fields = [
            "id", "category", "name", "slug", "description",
            "price", "discount_price", "sku", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate(self, attrs):
        discount_price = attrs.get("discount_price", getattr(self.instance, "discount_price", None))
        price = attrs.get("price", getattr(self.instance, "price", None))
        if discount_price is not None and price is not None and discount_price > price:
            raise serializers.ValidationError("discount_price cannot exceed price.")
        return attrs

    def create(self, validated_data):
        base_slug = slugify(validated_data["name"])[:210] or "product"
        slug = base_slug
        suffix = 2
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"[:220]
            suffix += 1
        return Product.objects.create(slug=slug, **validated_data)
