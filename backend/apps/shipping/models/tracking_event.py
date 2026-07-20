from django.db import models

from apps.shipping.models.shipment import Shipment


class ShipmentTrackingEvent(models.Model):
    """The append-only timeline that powers "live tracking" — each row
    is one status update with an optional location and note."""

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="tracking_events")
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=150, blank=True)
    note = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shipment_tracking_events"
        ordering = ["occurred_at"]

    def __str__(self):
        return f"{self.shipment_id}: {self.status}"
