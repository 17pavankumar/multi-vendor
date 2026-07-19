import django_filters

from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    """Exact/range filters for the browse page. Free-text search is
    handled separately by DRF's SearchFilter (see views/public.py) —
    keeping the two apart avoids both listening for the same query
    param name."""

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "vendor", "min_price", "max_price"]
