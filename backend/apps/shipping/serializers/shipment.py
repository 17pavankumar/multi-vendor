from rest_framework import serializers

from apps.orders.models import Order
from apps.shipping.models import Shipment, ShipmentTrackingEvent


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTrackingEvent
        fields = ["id", "status", "location", "note", "occurred_at"]
        read_only_fields = ["id", "occurred_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    """Read serializer — nests the full tracking timeline. Used both
    for a vendor's own shipment list and the customer-facing
    "track my order" endpoint."""

    tracking_events = TrackingEventSerializer(many=True, read_only=True)
    vendor_store_name = serializers.CharField(source="vendor.store_name", read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id", "order", "vendor", "vendor_store_name", "carrier", "tracking_number",
            "status", "shipped_at", "delivered_at", "estimated_delivery", "tracking_events",
        ]


class CreateShipmentSerializer(serializers.Serializer):
    """Input validation for POST /api/shipping/mine/ — apps.shipping.
    services.create_shipment does the actual work (and the ownership
    check: is this order actually one this vendor sold on)."""

    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    carrier = serializers.CharField(required=False, allow_blank=True, default="")
    tracking_number = serializers.CharField(required=False, allow_blank=True, default="")
    estimated_delivery = serializers.DateField(required=False, allow_null=True, default=None)


class AddTrackingEventSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.Status.choices)
    location = serializers.CharField(required=False, allow_blank=True, default="")
    note = serializers.CharField(required=False, allow_blank=True, default="")
