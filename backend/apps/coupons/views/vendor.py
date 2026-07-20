from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.coupons.models import Coupon
from apps.coupons.serializers import CouponSerializer


class VendorCouponViewSet(viewsets.ModelViewSet):
    """/api/coupons/mine/ — CRUD on the logged-in vendor's own coupons."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CouponSerializer

    def _vendor_profile(self):
        try:
            return self.request.user.vendor_profile
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("You don't have a vendor profile.") from exc

    def get_queryset(self):
        return Coupon.objects.filter(vendor=self._vendor_profile())

    def perform_create(self, serializer):
        serializer.save(vendor=self._vendor_profile())
