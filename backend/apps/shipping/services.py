from django.db import transaction
from django.utils import timezone

from apps.orders.models import OrderItem
from apps.shipping.models import Shipment, ShipmentTrackingEvent


class ShippingError(Exception):
    """Raised for shipment-creation/update failures — the view turns
    this into a 400 with the message as-is; nothing here talks HTTP."""


@transaction.atomic
def create_shipment(vendor, order, carrier="", tracking_number="", estimated_delivery=None):
    """Creating a shipment IS the "I've shipped this" action — there's
    no separate "mark as shipped" step. It immediately sets
    status=SHIPPED, bulk-updates every one of this vendor's items on
    the order to fulfillment_status=SHIPPED (keeping the per-item
    status and the shipment-level status from drifting apart), and logs
    the first tracking event."""
    items = OrderItem.objects.filter(order=order, vendor=vendor).exclude(
        fulfillment_status=OrderItem.FulfillmentStatus.CANCELLED
    )
    if not items.exists():
        raise ShippingError("This vendor has no items on this order.")
    if Shipment.objects.filter(order=order, vendor=vendor).exists():
        raise ShippingError("A shipment for this order already exists.")

    shipment = Shipment.objects.create(
        order=order,
        vendor=vendor,
        carrier=carrier,
        tracking_number=tracking_number,
        estimated_delivery=estimated_delivery,
        status=Shipment.Status.SHIPPED,
        shipped_at=timezone.now(),
    )
    items.update(fulfillment_status=OrderItem.FulfillmentStatus.SHIPPED)
    ShipmentTrackingEvent.objects.create(
        shipment=shipment, status=Shipment.Status.SHIPPED, note="Shipment created"
    )
    return shipment


@transaction.atomic
def add_tracking_event(shipment, status, location="", note=""):
    """Appends one entry to the timeline and updates the shipment's
    denormalized `status` to match. Reaching DELIVERED also stamps
    delivered_at and flips every item on this vendor's slice of the
    order to fulfillment_status=DELIVERED — which is what unlocks
    leaving a review (apps.reviews requires a delivered OrderItem)."""
    event = ShipmentTrackingEvent.objects.create(
        shipment=shipment, status=status, location=location, note=note
    )

    shipment.status = status
    update_fields = ["status"]
    if status == Shipment.Status.DELIVERED:
        shipment.delivered_at = timezone.now()
        update_fields.append("delivered_at")
        OrderItem.objects.filter(order=shipment.order, vendor=shipment.vendor).update(
            fulfillment_status=OrderItem.FulfillmentStatus.DELIVERED
        )
    shipment.save(update_fields=update_fields)

    return event
