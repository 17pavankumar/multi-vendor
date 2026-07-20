from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.serializers import VerifyPaymentSerializer
from apps.payments.services import verify_payment_signature


class VerifyPaymentView(APIView):
    """POST /api/payments/verify/ — called by the frontend right after
    Razorpay's checkout widget reports a successful payment, with the
    values its success callback provides. Confirms they're genuine
    before touching the order, and scopes the lookup to the caller's
    own orders so one user can't confirm (or probe the existence of)
    another user's payment."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            payment = Payment.objects.select_related("order").get(
                razorpay_order_id=data["razorpay_order_id"], order__user=request.user
            )
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        if not verify_payment_signature(
            data["razorpay_order_id"], data["razorpay_payment_id"], data["razorpay_signature"]
        ):
            payment.status = Payment.Status.FAILED
            payment.error_description = "Signature verification failed."
            payment.save(update_fields=["status", "error_description", "updated_at"])
            return Response(
                {"detail": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            payment.razorpay_payment_id = data["razorpay_payment_id"]
            payment.razorpay_signature = data["razorpay_signature"]
            payment.status = Payment.Status.CAPTURED
            payment.save(
                update_fields=["razorpay_payment_id", "razorpay_signature", "status", "updated_at"]
            )

            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=["status", "updated_at"])

        return Response({"detail": "Payment verified.", "order_status": payment.order.status})
