from decimal import Decimal

import pytest
from django.utils import timezone

from apps.commission.tests.conftest import place_delivered_order_on_date

pytestmark = pytest.mark.django_db


def test_requires_admin(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/commission/admin/reports/")

    assert response.status_code == 403


def test_report_aggregates_totals(api_client, admin_user, customer, address, vendor, category):
    place_delivered_order_on_date(customer, address, vendor, category, timezone.now(), price="100.00")
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/commission/admin/reports/")

    assert response.status_code == 200
    body = response.json()
    # do_checkout() bypasses the payments/verify step, so the order is
    # left at its immediate post-checkout status.
    assert body["orders_by_status"]["pending"] == 1
    assert Decimal(str(body["total_revenue"])) == Decimal("100.00")
    assert body["vendor_breakdown"][0]["vendor__store_name"] == vendor.store_name
    assert Decimal(str(body["vendor_breakdown"][0]["gross_sales"])) == Decimal("100.00")


def test_report_with_no_orders(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/commission/admin/reports/")

    assert response.status_code == 200
    body = response.json()
    assert body["total_revenue"] == 0
    assert body["total_commission_earned"] == 0
    assert body["vendor_breakdown"] == []
