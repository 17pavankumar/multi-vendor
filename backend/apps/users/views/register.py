from rest_framework import generics, permissions

from apps.users.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — open to anyone (no token yet, since
    the point of this endpoint is to obtain one). Creates a customer or
    vendor account; see RegisterSerializer.validate_role for why admin
    accounts can't be created here."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
