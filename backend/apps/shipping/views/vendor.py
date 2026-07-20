from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shipping.models import Shipment
from apps.shipping.serializers import AddTrackingEventSerializer, CreateShipmentSerializer, ShipmentSerializer
from apps.shipping.services import ShippingError, add_tracking_event, create_shipment


def _vendor_profile(request):
    try:
        return request.user.vendor_profile
    except ObjectDoesNotExist as exc:
        raise PermissionDenied("You don't have a vendor profile.") from exc


class VendorShipmentListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/shipping/mine/ — a vendor's own shipments. POSTing
    creates one (see services.create_shipment) — this IS "I've shipped
    this order," not a draft that gets shipped later."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(vendor=_vendor_profile(self.request)).prefetch_related(
            "tracking_events"
        )

    def get_serializer_class(self):
        return ShipmentSerializer if self.request.method == "GET" else CreateShipmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            shipment = create_shipment(
                vendor=_vendor_profile(request),
                order=data["order"],
                carrier=data["carrier"],
                tracking_number=data["tracking_number"],
                estimated_delivery=data["estimated_delivery"],
            )
        except ShippingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class VendorShipmentTrackingEventCreateView(APIView):
    """POST /api/shipping/mine/<pk>/events/ — add a tracking update to
    one of the vendor's own shipments."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        shipment = get_object_or_404(Shipment, pk=pk, vendor=_vendor_profile(request))
        serializer = AddTrackingEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_tracking_event(shipment, **serializer.validated_data)
        return Response(ShipmentSerializer(shipment).data)
