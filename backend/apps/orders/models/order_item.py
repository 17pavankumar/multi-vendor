from decimal import Decimal

from django.db import models

from apps.orders.models.order import Order
from apps.products.models import Product
from apps.vendors.models import VendorProfile


class OrderItem(models.Model):
    """A single vendor's line item within an order. A multi-vendor
    order has one OrderItem per (product, vendor) pair — this is what
    makes the order "multi-vendor": fulfillment and commission are
    tracked per line, not per order."""

    class FulfillmentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # A coupon discount is applied at the order level (Order.discount_amount),
    # not split proportionally across items — this column exists for
    # schema completeness and future per-item promotions, but checkout
    # (apps.orders.services) never writes a non-zero value here yet.
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Snapshotted from vendor.default_commission_rate at order time — if
    # the platform changes commission rates later, historical orders
    # still show what was actually charged.
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fulfillment_status = models.CharField(
        max_length=20, choices=FulfillmentStatus.choices, default=FulfillmentStatus.PENDING
    )

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.order.order_number})"
