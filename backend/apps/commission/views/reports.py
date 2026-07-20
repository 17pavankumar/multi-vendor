from django.db.models import Count, Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderItem
from apps.users.permissions import IsAdminRole


class PlatformReportView(APIView):
    """GET /api/commission/admin/reports/ — a snapshot of platform
    health: order counts by status, total revenue, total commission
    earned, and a per-vendor sales breakdown. Computed on every read,
    no caching or materialized view — fine at this project's scale,
    would need revisiting for a platform with millions of orders."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        orders_by_status = dict(
            Order.objects.values_list("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )
        order_totals = Order.objects.aggregate(total_revenue=Sum("total_amount"))
        commission_totals = OrderItem.objects.aggregate(total_commission=Sum("commission_amount"))

        vendor_breakdown = list(
            OrderItem.objects.values("vendor_id", "vendor__store_name")
            .annotate(
                gross_sales=Sum("subtotal"),
                commission_earned=Sum("commission_amount"),
                items_sold=Sum("quantity"),
            )
            .order_by("-gross_sales")
        )

        return Response(
            {
                "orders_by_status": orders_by_status,
                "total_revenue": order_totals["total_revenue"] or 0,
                "total_commission_earned": commission_totals["total_commission"] or 0,
                "vendor_breakdown": vendor_breakdown,
            }
        )
