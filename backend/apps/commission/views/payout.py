from django.utils import timezone
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.commission.models import VendorPayout
from apps.commission.serializers import GeneratePayoutsSerializer, VendorPayoutSerializer
from apps.commission.tasks import generate_vendor_payouts
from apps.users.permissions import IsAdminRole


class VendorPayoutListView(generics.ListAPIView):
    """GET /api/commission/admin/payouts/ — every payout batch, for
    admin review. ?vendor=<id> and ?status=<status> narrow it."""

    permission_classes = [IsAdminRole]
    serializer_class = VendorPayoutSerializer

    def get_queryset(self):
        queryset = VendorPayout.objects.select_related("vendor")
        vendor_id = self.request.query_params.get("vendor")
        status_filter = self.request.query_params.get("status")
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class GeneratePayoutsView(APIView):
    """POST /api/commission/admin/payouts/generate/ — runs payout
    generation synchronously (calling the task function directly, not
    via .delay()) so the admin gets the created payout batch back in
    the response immediately, instead of having to poll a task id."""

    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = GeneratePayoutsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payout_ids = generate_vendor_payouts(
            data["period_start"].isoformat(), data["period_end"].isoformat()
        )
        payouts = VendorPayout.objects.filter(pk__in=payout_ids)
        return Response(VendorPayoutSerializer(payouts, many=True).data, status=status.HTTP_201_CREATED)


class MarkPayoutPaidView(APIView):
    """POST /api/commission/admin/payouts/<pk>/mark-paid/"""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        payout = get_object_or_404(VendorPayout, pk=pk)
        payout.status = VendorPayout.Status.PAID
        payout.paid_at = timezone.now()
        payout.save(update_fields=["status", "paid_at"])
        return Response(VendorPayoutSerializer(payout).data)
