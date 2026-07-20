from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.orders.models import OrderItem
from apps.products.models import Product


class Review(models.Model):
    """order_item proves the reviewer actually bought and received the
    item — a "verified purchase" review. Set by the serializer (never
    client-writable), which looks up a delivered OrderItem for this
    user+product rather than trusting a client-supplied id (see
    serializers/review.py)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey(
        OrderItem, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    # Validators duplicate the DB-level chk_reviews_rating_range CHECK
    # constraint below on purpose: without them, an out-of-range rating
    # would only be caught at INSERT time as a raw IntegrityError (500),
    # instead of failing DRF's serializer validation cleanly (400).
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=150, blank=True)
    body = models.TextField(blank=True)
    # No moderation queue in this phase — every review is auto-approved.
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="uq_reviews_user_product"),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="chk_reviews_rating_range",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} rated {self.product.name} {self.rating}/5"
