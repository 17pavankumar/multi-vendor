import pytest

from apps.orders.models import OrderItem
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def _place_order(customer, address, vendor, category, **product_overrides):
    product = make_product(vendor, category, **product_overrides)
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    return do_checkout(customer, address)


def test_list_requires_authentication(api_client):
    response = api_client.get("/api/orders/vendor/")

    assert response.status_code == 401


def test_vendor_sees_only_own_sales(api_client, customer, address, vendor, pending_vendor, category):
    _place_order(customer, address, vendor, category)
    _place_order(customer, address, pending_vendor, category, name="Other", slug="other", sku="SKU-OTHER")

    api_client.force_authenticate(user=vendor.user)
    response = api_client.get("/api/orders/vendor/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["product_name"] == "Wireless Mouse"


def test_vendor_can_update_fulfillment_status(api_client, customer, address, vendor, category):
    _place_order(customer, address, vendor, category)
    item = OrderItem.objects.get(vendor=vendor)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        f"/api/orders/vendor/{item.pk}/", {"fulfillment_status": "packed"}, content_type="application/json"
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.fulfillment_status == "packed"


def test_vendor_cannot_update_another_vendors_item(
    api_client, customer, address, vendor, pending_vendor, category
):
    _place_order(customer, address, pending_vendor, category)
    item = OrderItem.objects.get(vendor=pending_vendor)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        f"/api/orders/vendor/{item.pk}/", {"fulfillment_status": "packed"}, content_type="application/json"
    )

    assert response.status_code == 404


def test_vendor_cannot_change_quantity_or_price(api_client, customer, address, vendor, category):
    _place_order(customer, address, vendor, category)
    item = OrderItem.objects.get(vendor=vendor)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        f"/api/orders/vendor/{item.pk}/",
        {"quantity": 999, "unit_price": "0.01"},
        content_type="application/json",
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.quantity == 1
    assert str(item.unit_price) == "19.99"
