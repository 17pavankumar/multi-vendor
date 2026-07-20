from datetime import timedelta

import pytest
from django.utils import timezone

from apps.coupons.models import Coupon

pytestmark = pytest.mark.django_db


def _payload(**overrides):
    now = timezone.now()
    payload = {
        "code": "SAVE10",
        "discount_type": "percent",
        "discount_value": "10.00",
        "valid_from": now.isoformat(),
        "valid_until": (now + timedelta(days=30)).isoformat(),
    }
    payload.update(overrides)
    return payload


def test_vendor_create_scopes_to_own_store(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post("/api/coupons/mine/", _payload())

    assert response.status_code == 201
    coupon = Coupon.objects.get(code="SAVE10")
    assert coupon.vendor_id == vendor.pk


def test_vendor_cannot_see_other_vendors_coupons(api_client, vendor, pending_vendor):
    Coupon.objects.create(
        vendor=pending_vendor,
        code="OTHER10",
        discount_type=Coupon.DiscountType.PERCENT,
        discount_value="10.00",
        valid_from=timezone.now(),
        valid_until=timezone.now() + timedelta(days=30),
    )
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/coupons/mine/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []


def test_admin_create_is_platform_wide(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post("/api/coupons/admin/", _payload(code="PLATFORM10"))

    assert response.status_code == 201
    coupon = Coupon.objects.get(code="PLATFORM10")
    assert coupon.vendor_id is None


def test_non_admin_cannot_access_admin_endpoint(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/coupons/admin/")

    assert response.status_code == 403


def test_invalid_date_range_rejected(api_client, vendor):
    now = timezone.now()
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(
        "/api/coupons/mine/",
        _payload(valid_from=now.isoformat(), valid_until=(now - timedelta(days=1)).isoformat()),
    )

    assert response.status_code == 400
