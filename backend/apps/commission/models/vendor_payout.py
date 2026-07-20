from django.db import models
from django.db.models import F, Q

from apps.vendors.models import VendorProfile


class VendorPayout(models.Model):
    """A periodic payout batch — what the platform owes a vendor after
    commission for a given date range. Created exclusively by
    apps.commission.tasks.generate_vendor_payouts (a Celery task,
    intended to run on a schedule — see CELERY_BEAT_SCHEDULE in
    settings.py); nothing else creates these rows."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="payouts")
    period_start = models.DateField()
    period_end = models.DateField()
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor_payouts"
        ordering = ["-period_start"]
        constraints = [
            models.CheckConstraint(condition=Q(period_end__gte=F("period_start")), name="chk_payout_period"),
        ]

    def __str__(self):
        return f"{self.vendor.store_name} {self.period_start}..{self.period_end}"
