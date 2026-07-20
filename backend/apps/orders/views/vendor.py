from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.orders.models import OrderItem
from apps.orders.serializers import VendorOrderItemSerializer


def _vendor_profile(request):
    try:
        return request.user.vendor_profile
    except ObjectDoesNotExist as exc:
        raise PermissionDenied("You don't have a vendor profile.") from exc


class VendorOrderItemListView(generics.ListAPIView):
    """GET /api/orders/vendor/ — every order line item sold through the
    logged-in vendor's store, across all customers' orders."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorOrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(vendor=_vendor_profile(self.request)).select_related(
            "order", "product", "order__user"
        )


class VendorOrderItemDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/orders/vendor/<pk>/ — a vendor can update
    fulfillment_status on their own line item; see
    VendorOrderItemSerializer for why nothing else on it is writable."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorOrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(vendor=_vendor_profile(self.request))
