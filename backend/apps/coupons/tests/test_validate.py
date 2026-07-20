from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.coupons.models import Coupon

pytestmark = pytest.mark.django_db


def _make_coupon(**overrides):
    now = timezone.now()
    defaults = {
        "code": "SAVE10",
        "discount_type": Coupon.DiscountType.PERCENT,
        "discount_value": Decimal("10.00"),
        "valid_from": now - timedelta(days=1),
        "valid_until": now + timedelta(days=1),
    }
    defaults.update(overrides)
    return Coupon.objects.create(**defaults)


def test_requires_authentication(api_client):
    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100"})

    assert response.status_code == 401


def test_percent_discount(api_client, customer):
    _make_coupon()
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "save10", "order_amount": "100.00"})

    assert response.status_code == 200
    assert response.json() == {"valid": True, "discount_amount": "10.00"}


def test_percent_discount_capped_by_max(api_client, customer):
    _make_coupon(discount_value=Decimal("50.00"), max_discount_amount=Decimal("20.00"))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "1000.00"})

    assert response.json()["discount_amount"] == "20.00"


def test_percent_discount_rounds_to_cents(api_client, customer):
    # 33.33% of $10.00 = $3.333 — must round to 2 decimal places, not
    # be returned as "3.3330".
    _make_coupon(discount_value=Decimal("33.33"))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "10.00"})

    assert response.json()["discount_amount"] == "3.33"


def test_fixed_discount(api_client, customer):
    _make_coupon(discount_type=Coupon.DiscountType.FIXED, discount_value=Decimal("15.00"))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100.00"})

    assert response.json()["discount_amount"] == "15.00"


def test_discount_never_exceeds_order_amount(api_client, customer):
    _make_coupon(discount_type=Coupon.DiscountType.FIXED, discount_value=Decimal("500.00"))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "20.00"})

    assert response.json()["discount_amount"] == "20.00"


def test_expired_coupon_is_invalid(api_client, customer):
    now = timezone.now()
    _make_coupon(valid_from=now - timedelta(days=10), valid_until=now - timedelta(days=1))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100.00"})

    assert response.status_code == 400
    assert response.json()["valid"] is False


def test_not_yet_active_coupon_is_invalid(api_client, customer):
    now = timezone.now()
    _make_coupon(valid_from=now + timedelta(days=1), valid_until=now + timedelta(days=10))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100.00"})

    assert response.status_code == 400


def test_inactive_coupon_is_invalid(api_client, customer):
    _make_coupon(is_active=False)
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100.00"})

    assert response.status_code == 400


def test_below_min_order_amount_is_invalid(api_client, customer):
    _make_coupon(min_order_amount=Decimal("50.00"))
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "10.00"})

    assert response.status_code == 400


def test_exhausted_usage_limit_is_invalid(api_client, customer):
    _make_coupon(usage_limit=5, usage_count=5)
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "SAVE10", "order_amount": "100.00"})

    assert response.status_code == 400


def test_nonexistent_code_returns_404(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/coupons/validate/", {"code": "NOPE", "order_amount": "100.00"})

    assert response.status_code == 404
