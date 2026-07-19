from rest_framework import generics, permissions

from apps.vendors.serializers import VendorApplicationSerializer


class VendorApplicationView(generics.CreateAPIView):
    """POST /api/vendors/apply/ — any authenticated user can apply;
    VendorApplicationSerializer itself blocks someone who already has a
    vendor_profile from applying a second time."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorApplicationSerializer
