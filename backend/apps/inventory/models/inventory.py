from django.db import models
from django.db.models import F, Q

from apps.products.models import Product


class Inventory(models.Model):
    """One row per product, created automatically the moment the
    product is (see signals.py) — never created or deleted directly
    through the API. Kept as its own table rather than columns on
    Product because stock changes at a much higher write frequency than
    product metadata, and reserved_quantity needs row-level locking
    during checkout without locking the whole product row."""

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory"
        verbose_name_plural = "inventory"
        constraints = [
            models.CheckConstraint(
                condition=Q(reserved_quantity__lte=F("quantity")), name="chk_reserved_lte_quantity"
            ),
        ]

    def __str__(self):
        return f"{self.product.name}: {self.quantity}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.low_stock_threshold
