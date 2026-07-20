from django.urls import path

from apps.orders.views import (
    CheckoutView,
    OrderDetailView,
    OrderListView,
    VendorOrderItemDetailView,
    VendorOrderItemListView,
)

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("vendor/", VendorOrderItemListView.as_view(), name="order-vendor-list"),
    path("vendor/<int:pk>/", VendorOrderItemDetailView.as_view(), name="order-vendor-detail"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("", OrderListView.as_view(), name="order-list"),
]
