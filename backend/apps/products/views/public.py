from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from apps.products.filters import ProductFilter
from apps.products.models import Product
from apps.products.serializers import ProductDetailSerializer, ProductListSerializer


def _visible_products():
    """Only products that are both live (status=active) AND belong to
    an approved vendor — a vendor's draft catalog, or any product from
    a still-pending/rejected/suspended vendor, never shows up publicly
    regardless of the product's own status."""
    return (
        Product.objects.filter(status=Product.Status.ACTIVE, vendor__status="approved")
        .select_related("vendor", "category")
        .prefetch_related("images")
    )


class ProductListView(generics.ListAPIView):
    """GET /api/products/ — supports ?category=<id>, ?vendor=<id>,
    ?min_price=, ?max_price= (see filters.py) and ?search= (free text
    over name/description)."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]

    def get_queryset(self):
        return _visible_products()


class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<slug>/"""

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return _visible_products()
