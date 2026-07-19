from django.contrib import admin

from apps.inventory.models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "reserved_quantity", "low_stock_threshold"]
    search_fields = ["product__name", "product__sku"]
