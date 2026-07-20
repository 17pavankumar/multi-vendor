from rest_framework import generics, permissions

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartItemSerializer


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartItemListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/cart/items/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart=_get_or_create_cart(self.request.user))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["cart"] = _get_or_create_cart(self.request.user)
        return context


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/cart/items/<pk>/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart=_get_or_create_cart(self.request.user))
