from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.vendors.models import VendorProfile


class Coupon(models.Model):
    """vendor=None means a platform-wide coupon issued by admin;
    vendor=<profile> means a vendor-specific one. Redeeming a coupon
    (incrementing usage_count, recording which order used it) happens
    at checkout — apps.coupons only owns validity rules and the
    read/write catalog of coupons themselves."""

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED = "fixed", "Fixed"

    vendor = models.ForeignKey(
        VendorProfile, null=True, blank=True, on_delete=models.CASCADE, related_name="coupons"
    )
    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    # Caps a percent discount, e.g. "20% off, up to $50". Unused for fixed discounts.
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  # None = unlimited
    usage_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupons"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(valid_until__gt=F("valid_from")), name="chk_coupon_dates"),
        ]

    def __str__(self):
        return self.code

    def compute_discount(self, order_amount):
        """Returns the discount amount for a given order subtotal, or
        None if the coupon doesn't currently apply (expired, not yet
        active, inactive, exhausted, or the order is below
        min_order_amount). Doesn't mutate anything — checking whether a
        coupon applies (apps.coupons.views.validate) and actually
        redeeming it (Phase 5's checkout) are deliberately separate
        operations."""
        now = timezone.now()
        if not self.is_active or not (self.valid_from <= now <= self.valid_until):
            return None
        if self.usage_limit is not None and self.usage_count >= self.usage_limit:
            return None
        if order_amount < self.min_order_amount:
            return None

        if self.discount_type == self.DiscountType.PERCENT:
            discount = order_amount * (self.discount_value / Decimal("100"))
            if self.max_discount_amount is not None:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value

        discount = min(discount, order_amount)
        # Percent math produces more than 2 decimal places (e.g.
        # 100.00 * 0.1 = 10.000) — money is always quantized to cents.
        return discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
