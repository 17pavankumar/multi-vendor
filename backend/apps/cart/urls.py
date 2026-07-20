from django.urls import path

from apps.cart.views import CartClearView, CartItemDetailView, CartItemListCreateView, CartView

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", CartItemListCreateView.as_view(), name="cart-item-list"),
    path("items/<int:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
]
