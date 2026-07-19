from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from apps.vendors.serializers import VendorProfileSerializer


class VendorProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/vendors/profile/ — the logged-in vendor's own
    store profile. Returns 404 (not 403) when the caller has no
    vendor_profile — from their point of view "you're not a vendor" and
    "your vendor record is missing" look the same, and 404 points them
    at /api/vendors/apply/ without leaking which case it is."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorProfileSerializer

    def get_object(self):
        try:
            return self.request.user.vendor_profile
        except ObjectDoesNotExist as exc:
            raise NotFound("No vendor profile yet — apply at /api/vendors/apply/.") from exc
