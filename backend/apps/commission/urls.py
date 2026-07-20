from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.commission.views import (
    CommissionRuleViewSet,
    GeneratePayoutsView,
    MarkPayoutPaidView,
    PlatformReportView,
    VendorPayoutListView,
)

router = SimpleRouter()
router.register("admin/rules", CommissionRuleViewSet, basename="commission-rule")

urlpatterns = [
    path("admin/payouts/generate/", GeneratePayoutsView.as_view(), name="payout-generate"),
    path("admin/payouts/<int:pk>/mark-paid/", MarkPayoutPaidView.as_view(), name="payout-mark-paid"),
    path("admin/payouts/", VendorPayoutListView.as_view(), name="payout-list"),
    path("admin/reports/", PlatformReportView.as_view(), name="platform-report"),
    path("", include(router.urls)),
]
