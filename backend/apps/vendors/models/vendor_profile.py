from decimal import Decimal

from django.conf import settings
from django.db import models


class VendorProfile(models.Model):
    """A store front, one-to-one with a User who has role="vendor".
    Created by the "apply to become a vendor" flow (see
    apps.vendors.serializers.application), starting in `status=pending`
    until an admin approves it (apps.vendors.views.approval)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    store_name = models.CharField(max_length=150)
    store_slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    default_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("10.00"))
    # Who last acted on this application (approved OR rejected) and when
    # — one pair of columns covers both decisions rather than doubling
    # up with separate rejected_by/rejected_at fields nothing else needs.
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vendor_approval_decisions",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendor_profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.store_name

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED
