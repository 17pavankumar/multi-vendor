from django.conf import settings
from django.db import models


class Address(models.Model):
    """A shipping/billing address owned by a user. A user can have several
    (home, office, ...); `is_default` marks the one checkout pre-selects."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # an address is meaningless without its owner
        related_name="addresses",
    )
    label = models.CharField(max_length=50, blank=True)  # "Home", "Office"
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2)  # ISO 3166-1 alpha-2
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"
        ordering = ["-is_default", "-created_at"]
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.line1}, {self.city} ({self.user.email})"
