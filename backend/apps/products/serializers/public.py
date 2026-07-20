from django.db.models import Avg
from rest_framework import serializers

from apps.products.models import Product
from apps.products.serializers.image import ProductImageSerializer


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight — used for the browse/search grid. `primary_image` is
    a single URL (or null), not the full images array: a grid of
    product cards only ever shows one thumbnail each. Relies on the
    view calling .prefetch_related("images") so this doesn't issue an
    extra query per product in the list."""

    vendor_store_name = serializers.CharField(source="vendor.store_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "discount_price",
            "vendor_store_name", "category_name", "primary_image",
        ]

    def get_primary_image(self, product):
        images = list(product.images.all())
        image = next((img for img in images if img.is_primary), images[0] if images else None)
        return image.image.url if image else None


class ProductDetailSerializer(serializers.ModelSerializer):
    vendor_store_name = serializers.CharField(source="vendor.store_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price", "discount_price", "sku",
            "vendor_store_name", "category_name", "images", "average_rating",
            "review_count", "created_at",
        ]

    def get_average_rating(self, product):
        # `product.reviews` is apps.reviews.Review's reverse accessor —
        # products deliberately has no import of apps.reviews at all;
        # Django wires the relation up via the app registry, so using
        # it here doesn't create a module-level dependency in either
        # direction between the two apps.
        result = product.reviews.filter(is_approved=True).aggregate(avg=Avg("rating"))["avg"]
        return round(result, 2) if result is not None else None

    def get_review_count(self, product):
        return product.reviews.filter(is_approved=True).count()
