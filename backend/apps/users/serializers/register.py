from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Handles POST /api/auth/register/. Accepts a plaintext password,
    runs it through Django's password validators (min length, not too
    common, not all-numeric, etc.), then hands off to UserManager so it
    gets hashed — this serializer never touches a raw password after
    validation."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "phone", "role"]
        extra_kwargs = {"role": {"required": False}}

    def validate_role(self, value):
        # Prevents "role": "admin" in a public registration payload from
        # minting an admin account — admin accounts are created only via
        # `createsuperuser` or by an existing admin, never self-service.
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("Cannot self-register as admin.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
