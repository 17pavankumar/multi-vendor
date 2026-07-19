import pytest

from apps.inventory.models import Inventory
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_inventory_row_created_automatically_with_product(vendor, category):
    product = make_product(vendor, category)

    assert Inventory.objects.filter(product=product).exists()
    assert product.inventory.quantity == 0


def test_list_requires_authentication(api_client):
    response = api_client.get("/api/inventory/mine/")

    assert response.status_code == 401


def test_vendor_sees_only_own_inventory(api_client, vendor, category):
    make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/inventory/mine/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["product_name"] == "Wireless Mouse"


def test_vendor_can_restock_quantity(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        f"/api/inventory/mine/{product.inventory.pk}/",
        {"quantity": 50, "low_stock_threshold": 10},
        content_type="application/json",
    )

    assert response.status_code == 200
    product.inventory.refresh_from_db()
    assert product.inventory.quantity == 50
    assert product.inventory.low_stock_threshold == 10


def test_reserved_quantity_is_read_only(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        f"/api/inventory/mine/{product.inventory.pk}/",
        {"reserved_quantity": 999},
        content_type="application/json",
    )

    assert response.status_code == 200
    product.inventory.refresh_from_db()
    assert product.inventory.reserved_quantity == 0


def test_vendor_cannot_see_another_vendors_inventory(api_client, vendor, pending_vendor, category):
    other_product = make_product(pending_vendor, category, slug="other", sku="SKU-OTHER")
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get(f"/api/inventory/mine/{other_product.inventory.pk}/")

    assert response.status_code == 404
