from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.inventory.models import Inventory
from apps.inventory.serializers import InventorySerializer


class VendorInventoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """/api/inventory/mine/ — list and update stock levels for the
    logged-in vendor's own products. No create or delete: every product
    gets exactly one Inventory row automatically the moment it's
    created (see apps.inventory.signals), and it's removed automatically
    with the product via OneToOneField(on_delete=CASCADE)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InventorySerializer

    def get_queryset(self):
        try:
            vendor_profile = self.request.user.vendor_profile
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("You don't have a vendor profile.") from exc
        return Inventory.objects.filter(product__vendor=vendor_profile).select_related("product")
