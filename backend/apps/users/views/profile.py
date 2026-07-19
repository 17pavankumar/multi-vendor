from rest_framework import generics, permissions

from apps.users.serializers import ProfileSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/ — always operates on the logged-in
    user's own record. No <id> in the URL on purpose: there's no reason
    for this endpoint to accept one, and leaving it out removes the
    need to check "is this id the caller's own id?" entirely."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user
