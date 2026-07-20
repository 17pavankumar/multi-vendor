from django.conf import settings
from django.db import models

from apps.coupons.models import Coupon
from apps.orders.models.order import Order


class CouponRedemption(models.Model):
    """Records that `coupon` was used on `order`, and for how much —
    needed to audit discount totals. db/schema.sql models this as
    UNIQUE(coupon_id, order_id); this simplifies that to a strict
    OneToOneField on `order`, since checkout (apps.orders.services)
    only ever accepts a single coupon code per order — a stricter
    version of the same constraint, not a looser one."""

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="redemptions")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="coupon_redemption")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_redemptions"
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupon_redemptions"

    def __str__(self):
        return f"{self.coupon.code} on {self.order.order_number}"
