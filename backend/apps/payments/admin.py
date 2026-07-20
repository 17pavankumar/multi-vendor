from django.contrib import admin

from apps.payments.models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["razorpay_order_id", "order", "status", "amount", "created_at"]
    list_filter = ["status"]
    search_fields = ["razorpay_order_id", "razorpay_payment_id", "order__order_number"]


admin.site.register(Refund)
