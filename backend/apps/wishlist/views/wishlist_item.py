from rest_framework import generics, permissions

from apps.wishlist.models import WishlistItem
from apps.wishlist.serializers import WishlistItemSerializer


class WishlistItemListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/wishlist/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)


class WishlistItemDeleteView(generics.DestroyAPIView):
    """DELETE /api/wishlist/<pk>/"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)
