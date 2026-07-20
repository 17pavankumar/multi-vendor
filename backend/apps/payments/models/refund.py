from django.db import models

from apps.payments.models.payment import Payment


class Refund(models.Model):
    """Modeled separately from Payment because Razorpay supports partial
    refunds — one payment can have several. No initiation endpoint
    exists yet in this phase (there's no "returns" workflow driving it
    yet); this is schema/model groundwork for that later feature."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="refunds")
    razorpay_refund_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refunds"

    def __str__(self):
        return self.razorpay_refund_id
