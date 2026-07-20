from rest_framework import generics, permissions

from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class OrderListView(generics.ListAPIView):
    """GET /api/orders/ — the logged-in customer's own order history."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/<pk>/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
