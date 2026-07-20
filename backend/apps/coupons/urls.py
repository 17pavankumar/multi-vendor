from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.coupons.views import AdminCouponViewSet, CouponValidateView, VendorCouponViewSet

router = SimpleRouter()
router.register("mine", VendorCouponViewSet, basename="coupon-mine")
router.register("admin", AdminCouponViewSet, basename="coupon-admin")

urlpatterns = [
    path("validate/", CouponValidateView.as_view(), name="coupon-validate"),
    path("", include(router.urls)),
]
