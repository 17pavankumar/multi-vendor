from django.urls import path

from apps.wishlist.views import WishlistItemDeleteView, WishlistItemListCreateView

urlpatterns = [
    path("", WishlistItemListCreateView.as_view(), name="wishlist-list"),
    path("<int:pk>/", WishlistItemDeleteView.as_view(), name="wishlist-detail"),
]
