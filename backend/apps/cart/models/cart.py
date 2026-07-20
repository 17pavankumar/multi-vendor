from decimal import Decimal

from django.conf import settings
from django.db import models


class Cart(models.Model):
    """One per user, created lazily on first access (see views/cart.py)
    rather than eagerly at registration — not every account (vendors,
    admins) ever shops."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart({self.user.email})"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))
