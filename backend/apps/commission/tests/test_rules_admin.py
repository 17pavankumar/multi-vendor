from decimal import Decimal

import pytest

from apps.commission.models import CommissionRule

pytestmark = pytest.mark.django_db


def test_create_requires_admin_role(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post("/api/commission/admin/rules/", {"rate": "5.00"})

    assert response.status_code == 403
    assert not CommissionRule.objects.exists()


def test_admin_can_create_platform_wide_rule(api_client, admin_user, category):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/commission/admin/rules/", {"category": category.pk, "rate": "3.50"}
    )

    assert response.status_code == 201
    rule = CommissionRule.objects.get(category=category)
    assert rule.vendor_id is None
    assert rule.rate == Decimal("3.50")


def test_admin_can_create_vendor_specific_rule(api_client, admin_user, vendor, category):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/commission/admin/rules/",
        {"vendor": vendor.pk, "category": category.pk, "rate": "1.00"},
    )

    assert response.status_code == 201
    rule = CommissionRule.objects.get(vendor=vendor, category=category)
    assert rule.rate == Decimal("1.00")


def test_admin_can_delete_rule(api_client, admin_user, category):
    rule = CommissionRule.objects.create(vendor=None, category=category, rate=Decimal("5.00"))
    api_client.force_authenticate(user=admin_user)

    response = api_client.delete(f"/api/commission/admin/rules/{rule.pk}/")

    assert response.status_code == 204
    assert not CommissionRule.objects.filter(pk=rule.pk).exists()


def test_list_requires_authentication(api_client):
    response = api_client.get("/api/commission/admin/rules/")

    assert response.status_code == 401
