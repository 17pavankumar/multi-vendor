from rest_framework import viewsets

from apps.coupons.models import Coupon
from apps.coupons.serializers import CouponSerializer
from apps.users.permissions import IsAdminRole


class AdminCouponViewSet(viewsets.ModelViewSet):
    """/api/coupons/admin/ — CRUD on platform-wide coupons (vendor is
    always null here; a vendor's own coupons live under /mine/ instead,
    see views/vendor.py)."""

    permission_classes = [IsAdminRole]
    serializer_class = CouponSerializer
    queryset = Coupon.objects.filter(vendor__isnull=True)

    def perform_create(self, serializer):
        serializer.save(vendor=None)
