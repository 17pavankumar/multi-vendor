from rest_framework import generics, permissions

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


class ProductReviewListView(generics.ListAPIView):
    """GET /api/reviews/product/<product_id>/ — public list of approved
    reviews for one product."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_id"], is_approved=True)


class ReviewCreateView(generics.CreateAPIView):
    """POST /api/reviews/ — authenticated, verified-purchase only (see
    ReviewSerializer.validate)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer


class MyReviewDeleteView(generics.DestroyAPIView):
    """DELETE /api/reviews/<pk>/ — a user can remove their own review."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
