from rest_framework import serializers

from apps.users.models import User


class ProfileSerializer(serializers.ModelSerializer):
    """Handles GET/PATCH on the logged-in user's own record. `role` is
    read-only here on purpose — changing your own role (e.g. customer
    -> admin) has to go through a separate, privileged flow, not a
    self-service profile edit."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "role", "is_verified", "created_at"]
        read_only_fields = ["id", "email", "role", "is_verified", "created_at"]
