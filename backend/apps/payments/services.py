import razorpay
from django.conf import settings

from apps.payments.models import Payment
from apps.payments.razorpay_client import get_client


def create_payment_for_order(order):
    """Creates a Razorpay order (their side, not ours — confusingly,
    "order" is also their term) and our local Payment record tracking
    it. Amount is in the smallest currency unit (paise for INR) per
    Razorpay's API — hence * 100."""
    client = get_client()
    razorpay_order = client.order.create(
        {"amount": int(order.total_amount * 100), "currency": "INR", "receipt": str(order.order_number)}
    )
    return Payment.objects.create(
        order=order, razorpay_order_id=razorpay_order["id"], amount=order.total_amount, currency="INR"
    )


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """True if the three values genuinely came from Razorpay for this
    payment (their SDK's HMAC check against our key secret), False
    otherwise. Used by views.verify right after the frontend's Razorpay
    checkout widget reports a successful payment — without this check,
    anyone could POST arbitrary values and mark an unpaid order paid."""
    client = get_client()
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False


def verify_webhook_signature(payload_body, received_signature):
    """Same idea as verify_payment_signature, but for Razorpay's own
    server-to-server webhook (views.webhook) rather than the frontend's
    callback — different secret (RAZORPAY_WEBHOOK_SECRET), different
    payload shape. `payload_body` must be the raw request body decoded
    to str: the SDK's HMAC implementation encodes it back to bytes
    itself and errors if handed bytes twice."""
    client = get_client()
    try:
        client.utility.verify_webhook_signature(
            payload_body, received_signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
