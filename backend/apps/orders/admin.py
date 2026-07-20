from django.contrib import admin

from apps.orders.models import CouponRedemption, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "status", "total_amount", "placed_at"]
    list_filter = ["status"]
    search_fields = ["order_number", "user__email"]
    inlines = [OrderItemInline]


admin.site.register(CouponRedemption)
