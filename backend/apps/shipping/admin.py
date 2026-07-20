from django.contrib import admin

from apps.shipping.models import Shipment, ShipmentTrackingEvent


class TrackingEventInline(admin.TabularInline):
    model = ShipmentTrackingEvent
    extra = 0


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["order", "vendor", "status", "carrier", "tracking_number"]
    list_filter = ["status"]
    search_fields = ["order__order_number", "tracking_number"]
    inlines = [TrackingEventInline]
