from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from apps.products.models import Product, ProductImage
from apps.products.serializers import ProductImageSerializer


class _OwnedProductMixin:
    """Resolves the product from the URL and confirms it belongs to the
    logged-in vendor — shared by both views below so the ownership
    check can't drift between list/create and detail/delete."""

    def get_product(self):
        try:
            vendor_profile = self.request.user.vendor_profile
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("You don't have a vendor profile.") from exc
        return get_object_or_404(Product, pk=self.kwargs["product_id"], vendor=vendor_profile)


class ProductImageListCreateView(_OwnedProductMixin, generics.ListCreateAPIView):
    """GET/POST /api/products/mine/<product_id>/images/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product=self.get_product())

    def perform_create(self, serializer):
        serializer.save(product=self.get_product())


class ProductImageDetailView(_OwnedProductMixin, generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/products/mine/<product_id>/images/<pk>/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product=self.get_product())
