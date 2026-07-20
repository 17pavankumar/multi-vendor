from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from apps.products.filters import ProductFilter
from apps.products.selectors import visible_products
from apps.products.serializers import ProductDetailSerializer, ProductListSerializer


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
        return visible_products().prefetch_related("images")


class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<slug>/"""

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return visible_products().prefetch_related("images")
