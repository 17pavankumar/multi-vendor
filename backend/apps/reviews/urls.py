from django.urls import path

from apps.reviews.views import MyReviewDeleteView, ProductReviewListView, ReviewCreateView

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="review-create"),
    path("product/<int:product_id>/", ProductReviewListView.as_view(), name="review-product-list"),
    path("<int:pk>/", MyReviewDeleteView.as_view(), name="review-delete"),
]
