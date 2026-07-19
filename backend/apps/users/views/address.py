from rest_framework import permissions, viewsets

from apps.users.models import Address
from apps.users.serializers import AddressSerializer


class AddressViewSet(viewsets.ModelViewSet):
    """/api/auth/addresses/ — full CRUD (list, create, retrieve, update,
    delete) via DRF's router, scoped to the logged-in user's own
    addresses only. get_queryset filtering (not a URL-level user id) is
    what makes it impossible for one user to read or edit another's
    address by guessing an id."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
