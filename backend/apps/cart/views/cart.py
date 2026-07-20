from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartSerializer


class CartView(generics.RetrieveAPIView):
    """GET /api/cart/ — the logged-in user's cart, auto-created here on
    first access rather than at registration time."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartClearView(APIView):
    """DELETE /api/cart/clear/ — empties the cart in one call, instead
    of making the client delete every line item individually."""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
