from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.services import verify_webhook_signature


class RazorpayWebhookView(APIView):
    """POST /api/payments/webhook/ — Razorpay's own server-to-server
    callback, as opposed to views.verify (which the frontend calls
    directly after its checkout widget succeeds). Public: Razorpay
    isn't a logged-in user, so this trusts the HMAC signature in the
    X-Razorpay-Signature header — verified against RAZORPAY_WEBHOOK_SECRET,
    a different secret from the one views.verify checks against —
    instead of a JWT."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        signature = request.headers.get("X-Razorpay-Signature", "")
        if not verify_webhook_signature(request.body.decode("utf-8"), signature):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event = request.data.get("event")
        payload = request.data.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payload.get("order_id")

        try:
            payment = Payment.objects.select_related("order").get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            # Unknown order — acknowledge anyway so Razorpay doesn't
            # keep retrying a webhook we have nothing to do with.
            return Response(status=status.HTTP_200_OK)

        if event == "payment.captured":
            payment.razorpay_payment_id = payload.get("id", "")
            payment.method = payload.get("method", "")
            payment.status = Payment.Status.CAPTURED
            payment.save(update_fields=["razorpay_payment_id", "method", "status", "updated_at"])
            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=["status", "updated_at"])
        elif event == "payment.failed":
            payment.status = Payment.Status.FAILED
            payment.error_code = payload.get("error_code", "")
            payment.error_description = payload.get("error_description", "")
            payment.save(update_fields=["status", "error_code", "error_description", "updated_at"])

        return Response(status=status.HTTP_200_OK)
