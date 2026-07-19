from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import RoleTokenObtainPairSerializer


class RoleTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/ with {email, password} -> {access, refresh}.
    Identical to simplejwt's built-in view (which already permits
    unauthenticated access, since obtaining a token is the whole point),
    just swapped to the serializer that embeds `role` in the token
    payload — see serializers/token.py."""

    serializer_class = RoleTokenObtainPairSerializer
