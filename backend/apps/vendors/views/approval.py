from django.utils import timezone
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminRole
from apps.vendors.models import VendorProfile
from apps.vendors.serializers import VendorAdminListSerializer


class VendorAdminListView(generics.ListAPIView):
    """GET /api/vendors/admin/ — every vendor application, for admins to
    review. ?status=pending narrows it to the approval queue."""

    permission_classes = [IsAdminRole]
    serializer_class = VendorAdminListSerializer

    def get_queryset(self):
        queryset = VendorProfile.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class _VendorDecisionView(APIView):
    """Shared body for approve/reject — same fields change either way,
    only the target status differs (set by the subclass)."""

    permission_classes = [IsAdminRole]
    target_status = None

    def post(self, request, pk):
        profile = get_object_or_404(VendorProfile, pk=pk)
        profile.status = self.target_status
        profile.approved_by = request.user
        profile.approved_at = timezone.now()
        profile.save(update_fields=["status", "approved_by", "approved_at"])
        return Response(VendorAdminListSerializer(profile).data)


class VendorApproveView(_VendorDecisionView):
    """POST /api/vendors/admin/<pk>/approve/"""

    target_status = VendorProfile.Status.APPROVED


class VendorRejectView(_VendorDecisionView):
    """POST /api/vendors/admin/<pk>/reject/"""

    target_status = VendorProfile.Status.REJECTED
