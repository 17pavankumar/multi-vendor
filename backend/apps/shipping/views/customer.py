from rest_framework import generics, permissions

from apps.shipping.models import Shipment
from apps.shipping.serializers import ShipmentSerializer


class OrderShipmentListView(generics.ListAPIView):
    """GET /api/shipping/order/<order_id>/ — "track my order": every
    shipment (one per vendor) for one of the caller's own orders."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        return Shipment.objects.filter(
            order_id=self.kwargs["order_id"], order__user=self.request.user
        ).prefetch_related("tracking_events")
