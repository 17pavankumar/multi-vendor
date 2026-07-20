from datetime import timedelta

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.commission.models import VendorPayout
from apps.orders.models import OrderItem
from apps.vendors.models import VendorProfile


@shared_task
def generate_vendor_payouts(period_start, period_end):
    """Sums every DELIVERED order item's subtotal/commission per vendor
    within [period_start, period_end] (both ISO date strings — Celery
    task arguments must be JSON-serializable), creating one
    VendorPayout row per vendor that had any sales in that window.

    Calling this function directly (not via .delay()/.apply_async())
    runs it synchronously in-process — exactly what the admin API's
    "generate now" endpoint does (apps.commission.views.payout), and
    what the tests do, neither needing a running Celery worker or
    broker. celery beat (see CELERY_BEAT_SCHEDULE in settings.py) is
    what actually dispatches it asynchronously on a schedule in
    production.

    Not idempotent per (vendor, period) — nothing stops two calls for
    the same range from creating two payouts. That's acceptable for a
    beat-scheduled task that runs once a week for the week that just
    ended, but is exactly why the admin-facing generate endpoint isn't
    something to click twice.
    """
    rows = (
        OrderItem.objects.filter(
            fulfillment_status=OrderItem.FulfillmentStatus.DELIVERED,
            order__placed_at__date__gte=period_start,
            order__placed_at__date__lte=period_end,
        )
        .values("vendor")
        .annotate(gross=Sum("subtotal"), commission=Sum("commission_amount"))
    )

    created_ids = []
    for row in rows:
        vendor = VendorProfile.objects.get(pk=row["vendor"])
        gross = row["gross"] or 0
        commission = row["commission"] or 0
        payout = VendorPayout.objects.create(
            vendor=vendor,
            period_start=period_start,
            period_end=period_end,
            gross_amount=gross,
            commission_amount=commission,
            net_amount=gross - commission,
        )
        created_ids.append(payout.pk)
    return created_ids


@shared_task
def generate_last_weeks_payouts():
    """What celery beat actually schedules — CELERY_BEAT_SCHEDULE
    entries can only pass static args, but a payout period needs to be
    computed relative to "now" each time it runs. Wraps
    generate_vendor_payouts with the 7 days ending yesterday."""
    period_end = timezone.now().date() - timedelta(days=1)
    period_start = period_end - timedelta(days=6)
    return generate_vendor_payouts(period_start.isoformat(), period_end.isoformat())
