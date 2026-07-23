import razorpay
from django.conf import settings
from django.db import transaction
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
            # checkout() has its own @transaction.atomic, but that
            # commits as soon as it returns — by itself it can't protect
            # against create_payment_for_order() failing right after.
            # Wrapping both in one outer atomic() turns checkout()'s
            # transaction into a savepoint: if Razorpay's API call
            # fails below, everything (the order, its items, the
            # inventory reservation) rolls back together, instead of
            # leaving an orphaned "pending" order with stock reserved
            # and no way to pay for it. Found by browser-testing this
            # flow with placeholder Razorpay credentials — every
            # backend test for this path mocks Razorpay, so this
            # failure mode was never exercised until then.
            with transaction.atomic():
                order = checkout(
                    user=request.user,
                    shipping_address_id=data["shipping_address_id"],
                    billing_address_id=data["billing_address_id"],
                    coupon_code=data.get("coupon_code") or None,
                )
                payment = create_payment_for_order(order)
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (razorpay.errors.BadRequestError, razorpay.errors.GatewayError, razorpay.errors.ServerError):
            # Covers a rejected/misconfigured API key (BadRequestError —
            # what actually happened when this was found: placeholder
            # dev credentials), a malformed response, or Razorpay's API
            # being down. All roll back the same way; the customer just
            # sees a clean, retryable error either way.
            return Response(
                {"detail": "Payment provider is temporarily unavailable. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

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
