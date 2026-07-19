from django.urls import path

from apps.vendors.views import (
    VendorAdminListView,
    VendorApplicationView,
    VendorApproveView,
    VendorProfileView,
    VendorRejectView,
)

urlpatterns = [
    path("apply/", VendorApplicationView.as_view(), name="vendor-apply"),
    path("profile/", VendorProfileView.as_view(), name="vendor-profile"),
    path("admin/", VendorAdminListView.as_view(), name="vendor-admin-list"),
    path("admin/<int:pk>/approve/", VendorApproveView.as_view(), name="vendor-admin-approve"),
    path("admin/<int:pk>/reject/", VendorRejectView.as_view(), name="vendor-admin-reject"),
]
