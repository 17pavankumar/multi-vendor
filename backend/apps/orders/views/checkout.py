from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.serializers import CheckoutSerializer, OrderSerializer
from apps.orders.services import CheckoutError, checkout
from apps.payments.services import create_payment_for_order


class CheckoutView(APIView):
    """POST /api/orders/checkout/ — turns the logged-in user's cart into
    an Order plus a Razorpay payment order in one call. Returns enough
    for the frontend to open Razorpay's checkout widget immediately;
    the widget's success callback then hits
    /api/payments/verify/ (apps.payments.views.verify) to confirm it."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = checkout(
                user=request.user,
                shipping_address_id=data["shipping_address_id"],
                billing_address_id=data["billing_address_id"],
                coupon_code=data.get("coupon_code") or None,
            )
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        payment = create_payment_for_order(order)

        return Response(
            {
                "order": OrderSerializer(order).data,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": payment.razorpay_order_id,
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
            status=status.HTTP_201_CREATED,
        )
