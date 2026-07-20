from rest_framework import serializers

from apps.orders.models import OrderItem
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Create/read a review. `order_item` and `is_approved` are never
    client-writable — validate() finds and attaches the caller's own
    delivered OrderItem for this product itself, proving it's a
    verified purchase rather than trusting a client-supplied id."""

    customer_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "customer_name", "rating", "title", "body", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs["product"]

        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You've already reviewed this product.")

        order_item = (
            OrderItem.objects.filter(
                order__user=user,
                product=product,
                fulfillment_status=OrderItem.FulfillmentStatus.DELIVERED,
            )
            .order_by("-id")
            .first()
        )
        if order_item is None:
            raise serializers.ValidationError("You can only review products from a delivered order.")

        attrs["order_item"] = order_item
        return attrs

    def create(self, validated_data):
        return Review.objects.create(user=self.context["request"].user, **validated_data)
