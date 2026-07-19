from rest_framework import serializers

from apps.products.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Used both to read images (nested inside ProductDetailSerializer)
    and for the vendor upload endpoint. `image_url` accepts a multipart
    file on write and returns the stored file's URL on read — the
    underlying model field is named `image` (an ImageField); this is
    just the external name it's exposed under, matching
    db/schema.sql's image_url column. `product` is deliberately not a
    field here — the view resolves it from the URL and supplies it via
    serializer.save(product=...), so a vendor can never attach an image
    to someone else's product by passing a different id."""

    image_url = serializers.ImageField(source="image", use_url=True)

    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "alt_text", "is_primary", "sort_order"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        if validated_data.get("is_primary"):
            ProductImage.objects.filter(product=validated_data["product"], is_primary=True).update(
                is_primary=False
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_primary"):
            (
                ProductImage.objects.filter(product=instance.product, is_primary=True)
                .exclude(pk=instance.pk)
                .update(is_primary=False)
            )
        return super().update(instance, validated_data)
