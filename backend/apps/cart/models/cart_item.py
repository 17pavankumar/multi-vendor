from django.core.validators import MinValueValidator
from django.db import models

from apps.cart.models.cart import Cart
from apps.products.models import Product


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="+")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Snapshotted at add-to-cart time so a vendor changing the price
    # mid-session doesn't silently change what's already in a
    # customer's cart.
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uq_cart_items_cart_product"),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
