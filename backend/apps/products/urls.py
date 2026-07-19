from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.products.views import (
    ProductDetailView,
    ProductImageDetailView,
    ProductImageListCreateView,
    ProductListView,
    VendorProductViewSet,
)

router = SimpleRouter()
router.register("mine", VendorProductViewSet, basename="product-mine")

urlpatterns = [
    # SimpleRouter (not DefaultRouter — its auto-generated root view
    # would collide with ProductListView; see the note in
    # apps/categories/urls.py for the full explanation).
    #
    # The image paths and the router ("mine/...") must come before the
    # <slug:slug>/ catch-all below — "mine" is itself a valid slug, and
    # would otherwise be swallowed by ProductDetailView first.
    path("mine/<int:product_id>/images/", ProductImageListCreateView.as_view(), name="product-image-list"),
    path(
        "mine/<int:product_id>/images/<int:pk>/",
        ProductImageDetailView.as_view(),
        name="product-image-detail",
    ),
    path("", include(router.urls)),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("", ProductListView.as_view(), name="product-list"),
]
