from django.urls import path

from apps.shipping.views import (
    OrderShipmentListView,
    VendorShipmentListCreateView,
    VendorShipmentTrackingEventCreateView,
)

urlpatterns = [
    path("mine/", VendorShipmentListCreateView.as_view(), name="shipment-mine-list"),
    path(
        "mine/<int:pk>/events/",
        VendorShipmentTrackingEventCreateView.as_view(),
        name="shipment-mine-events",
    ),
    path("order/<int:order_id>/", OrderShipmentListView.as_view(), name="shipment-order-list"),
]
