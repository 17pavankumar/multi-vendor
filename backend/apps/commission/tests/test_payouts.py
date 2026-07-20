from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.commission.models import VendorPayout
from apps.commission.tasks import generate_vendor_payouts
from apps.commission.tests.conftest import place_delivered_order_on_date
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_generate_creates_one_payout_per_vendor_with_sales(customer, address, vendor, category):
    now = timezone.now()
    place_delivered_order_on_date(customer, address, vendor, category, now, price="100.00")

    period_start = (now - timedelta(days=1)).date().isoformat()
    period_end = (now + timedelta(days=1)).date().isoformat()
    created_ids = generate_vendor_payouts(period_start, period_end)

    assert len(created_ids) == 1
    payout = VendorPayout.objects.get(pk=created_ids[0])
    assert payout.vendor == vendor
    assert payout.gross_amount == Decimal("100.00")
    assert payout.commission_amount == (Decimal("100.00") * vendor.default_commission_rate / 100).quantize(
        Decimal("0.01")
    )
    assert payout.net_amount == payout.gross_amount - payout.commission_amount


def test_generate_excludes_non_delivered_items(customer, address, vendor, category):
    product = make_product(vendor, category, price="50.00")
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    do_checkout(customer, address)  # left at fulfillment_status=pending, never marked delivered

    today = timezone.now().date().isoformat()
    created_ids = generate_vendor_payouts(today, today)

    assert created_ids == []


def test_generate_excludes_items_outside_period(customer, address, vendor, category):
    old_date = timezone.now() - timedelta(days=30)
    place_delivered_order_on_date(customer, address, vendor, category, old_date, price="75.00")

    today = timezone.now().date().isoformat()
    created_ids = generate_vendor_payouts(today, today)

    assert created_ids == []


def test_generate_sums_multiple_delivered_orders_for_same_vendor(customer, address, vendor, category):
    now = timezone.now()
    place_delivered_order_on_date(
        customer, address, vendor, category, now, price="20.00", slug="p1", sku="SKU-1"
    )
    place_delivered_order_on_date(
        customer, address, vendor, category, now, price="30.00", slug="p2", sku="SKU-2"
    )

    period = now.date().isoformat()
    created_ids = generate_vendor_payouts(period, period)

    assert len(created_ids) == 1
    payout = VendorPayout.objects.get(pk=created_ids[0])
    assert payout.gross_amount == Decimal("50.00")


def test_generate_endpoint_requires_admin(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(
        "/api/commission/admin/payouts/generate/",
        {"period_start": "2026-01-01", "period_end": "2026-01-07"},
    )

    assert response.status_code == 403


def test_generate_endpoint_rejects_backwards_range(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/commission/admin/payouts/generate/",
        {"period_start": "2026-01-07", "period_end": "2026-01-01"},
    )

    assert response.status_code == 400


def test_generate_endpoint_returns_created_payouts(
    api_client, admin_user, customer, address, vendor, category
):
    now = timezone.now()
    place_delivered_order_on_date(customer, address, vendor, category, now)
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/commission/admin/payouts/generate/",
        {
            "period_start": (now - timedelta(days=1)).date().isoformat(),
            "period_end": (now + timedelta(days=1)).date().isoformat(),
        },
    )

    assert response.status_code == 201
    assert len(response.json()) == 1
    assert response.json()[0]["vendor_store_name"] == vendor.store_name


def test_mark_paid(api_client, admin_user, vendor):
    payout = VendorPayout.objects.create(
        vendor=vendor,
        period_start="2026-01-01",
        period_end="2026-01-07",
        gross_amount=Decimal("100.00"),
        commission_amount=Decimal("10.00"),
        net_amount=Decimal("90.00"),
    )
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(f"/api/commission/admin/payouts/{payout.pk}/mark-paid/")

    assert response.status_code == 200
    payout.refresh_from_db()
    assert payout.status == VendorPayout.Status.PAID
    assert payout.paid_at is not None


def test_mark_paid_requires_admin(api_client, vendor):
    payout = VendorPayout.objects.create(
        vendor=vendor,
        period_start="2026-01-01",
        period_end="2026-01-07",
        gross_amount=Decimal("100.00"),
        commission_amount=Decimal("10.00"),
        net_amount=Decimal("90.00"),
    )
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(f"/api/commission/admin/payouts/{payout.pk}/mark-paid/")

    assert response.status_code == 403


def test_list_filters_by_status(api_client, admin_user, vendor):
    VendorPayout.objects.create(
        vendor=vendor, period_start="2026-01-01", period_end="2026-01-07",
        gross_amount=10, commission_amount=1, net_amount=9, status=VendorPayout.Status.PENDING,
    )
    VendorPayout.objects.create(
        vendor=vendor, period_start="2026-01-08", period_end="2026-01-14",
        gross_amount=10, commission_amount=1, net_amount=9, status=VendorPayout.Status.PAID,
    )
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/commission/admin/payouts/?status=paid")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["status"] == "paid"
