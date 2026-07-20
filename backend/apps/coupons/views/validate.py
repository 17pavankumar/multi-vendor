from decimal import Decimal, InvalidOperation

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.coupons.models import Coupon


class CouponValidateView(APIView):
    """POST /api/coupons/validate/ {code, order_amount} — checks whether
    a coupon can be applied right now, without redeeming it. Redemption
    (incrementing usage_count, recording which order used it) happens at
    checkout in Phase 5, alongside creating the order — a coupon being
    "valid" here is a preview, not a reservation."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "")
        try:
            order_amount = Decimal(str(request.data.get("order_amount", "0")))
        except InvalidOperation:
            return Response(
                {"valid": False, "detail": "order_amount must be a number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response(
                {"valid": False, "detail": "Coupon not found."}, status=status.HTTP_404_NOT_FOUND
            )

        discount = coupon.compute_discount(order_amount)
        if discount is None:
            return Response(
                {"valid": False, "detail": "This coupon isn't applicable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"valid": True, "discount_amount": str(discount)})
