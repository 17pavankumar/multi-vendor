from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.products.models import Product
from apps.products.serializers import VendorProductSerializer


class VendorProductViewSet(viewsets.ModelViewSet):
    """/api/products/mine/ — full CRUD on the logged-in vendor's own
    catalog, in any status (draft/active/archived). Unlike the public
    endpoints, which only ever surface status=active products from
    approved vendors, this shows everything the vendor owns regardless
    of status — including drafts they're still preparing."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorProductSerializer

    def _vendor_profile(self):
        try:
            return self.request.user.vendor_profile
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("You don't have a vendor profile.") from exc

    def get_queryset(self):
        return Product.objects.filter(vendor=self._vendor_profile())

    def perform_create(self, serializer):
        serializer.save(vendor=self._vendor_profile())
