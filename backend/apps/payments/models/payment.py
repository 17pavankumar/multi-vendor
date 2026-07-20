from django.db import models


class Payment(models.Model):
    """Razorpay's flow is: create an `order` on Razorpay's side first
    (razorpay_order_id, done at checkout — see apps.orders.views.checkout),
    collect payment client-side via their widget, then confirm it —
    either the frontend calling views.verify with the widget's success
    callback values, or Razorpay's own server-to-server webhook
    (views.webhook). Either path fills in razorpay_payment_id and
    razorpay_signature and flips status to captured."""

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payments")
    razorpay_order_id = models.CharField(max_length=64, unique=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)
    razorpay_signature = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    method = models.CharField(max_length=30, blank=True)  # card, upi, netbanking, wallet — from Razorpay
    error_code = models.CharField(max_length=50, blank=True)
    error_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.razorpay_order_id} ({self.status})"
