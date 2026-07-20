from django.contrib import admin

from apps.commission.models import CommissionRule, VendorPayout


@admin.register(CommissionRule)
class CommissionRuleAdmin(admin.ModelAdmin):
    list_display = ["vendor", "category", "rate"]


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ["vendor", "period_start", "period_end", "net_amount", "status"]
    list_filter = ["status"]
