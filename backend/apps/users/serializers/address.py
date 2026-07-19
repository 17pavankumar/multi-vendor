from rest_framework import serializers

from apps.users.models import Address


class AddressSerializer(serializers.ModelSerializer):
    """CRUD for a single address, always scoped to the logged-in user
    (the view supplies `request.user` — see views/address.py). Handles
    the "only one default address" rule here rather than in a DB
    constraint, since it depends on unsetting *other* rows, not just
    validating the one being written."""

    class Meta:
        model = Address
        fields = [
            "id", "label", "line1", "line2", "city", "state",
            "postal_code", "country", "is_default", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        if validated_data.get("is_default"):
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return Address.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_default"):
            (
                Address.objects.filter(user=instance.user, is_default=True)
                .exclude(pk=instance.pk)
                .update(is_default=False)
            )
        return super().update(instance, validated_data)
