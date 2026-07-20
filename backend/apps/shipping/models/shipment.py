from django.db import models

from apps.orders.models import Order
from apps.vendors.models import VendorProfile


class Shipment(models.Model):
    """One shipment per vendor per order — a multi-vendor order ships as
    N separate packages, so this table has no direct FK to order_items;
    it implicitly covers "every item this vendor sold within this
    order." `status` is a denormalized "current status" column, kept in
    sync with the latest ShipmentTrackingEvent (see services.py) so a
    reader doesn't have to scan the whole timeline just to know where a
    package currently is."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SHIPPED = "shipped", "Shipped"
        IN_TRANSIT = "in_transit", "In Transit"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.PROTECT, related_name="shipments")
    carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "shipments"
        constraints = [
            models.UniqueConstraint(fields=["order", "vendor"], name="uq_shipments_order_vendor"),
        ]

    def __str__(self):
        return f"Shipment({self.order.order_number}, {self.vendor.store_name})"
