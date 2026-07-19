from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Same login contract as simplejwt's default serializer, but embeds
    `role` and `email` directly in the JWT payload. Lets the React app
    decode the access token and route straight to the right dashboard
    (customer/vendor/admin) without an extra round-trip to /profile/."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token
