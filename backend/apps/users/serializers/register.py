from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Handles POST /api/auth/register/. Accepts a plaintext password,
    runs it through Django's password validators (min length, not too
    common, not all-numeric, etc.), then hands off to UserManager so it
    gets hashed — this serializer never touches a raw password after
    validation.

    Every account created here is a customer — `role` is deliberately
    not a field on this serializer at all (not even writable), so a
    posted "role" is silently ignored by DRF rather than needing a
    validator to reject it. Becoming a vendor is a separate, two-step
    flow (see apps.vendors: POST /api/vendors/apply/ creates a
    VendorProfile and flips User.role to "vendor" together, atomically)
    — a bare role flip with no VendorProfile row would leave the
    account in a state nothing else in the system expects."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "phone"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
