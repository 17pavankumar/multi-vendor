import pytest

from apps.orders.models import OrderItem
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product
from apps.shipping.models import Shipment

pytestmark = pytest.mark.django_db


def _place_order(customer, address, vendor, category, **product_overrides):
    product = make_product(vendor, category, **product_overrides)
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    return do_checkout(customer, address)


def test_create_shipment_requires_authentication(api_client):
    response = api_client.post("/api/shipping/mine/", {"order": 1})

    assert response.status_code == 401


def test_vendor_create_shipment(api_client, customer, address, vendor, category):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(
        "/api/shipping/mine/",
        {"order": order.pk, "carrier": "DHL", "tracking_number": "TRACK123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "shipped"
    assert body["tracking_number"] == "TRACK123"
    assert len(body["tracking_events"]) == 1

    item = OrderItem.objects.get(order=order, vendor=vendor)
    assert item.fulfillment_status == OrderItem.FulfillmentStatus.SHIPPED


def test_cannot_create_duplicate_shipment(api_client, customer, address, vendor, category):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)
    api_client.post("/api/shipping/mine/", {"order": order.pk})

    response = api_client.post("/api/shipping/mine/", {"order": order.pk})

    assert response.status_code == 400
    assert Shipment.objects.filter(order=order, vendor=vendor).count() == 1


def test_vendor_cannot_ship_order_with_no_items_from_them(
    api_client, customer, address, vendor, pending_vendor, category
):
    order = _place_order(customer, address, pending_vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post("/api/shipping/mine/", {"order": order.pk})

    assert response.status_code == 400
    assert not Shipment.objects.filter(order=order, vendor=vendor).exists()


def test_add_tracking_event_updates_status(api_client, customer, address, vendor, category):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)
    created = api_client.post("/api/shipping/mine/", {"order": order.pk})
    shipment_id = created.json()["id"]

    response = api_client.post(
        f"/api/shipping/mine/{shipment_id}/events/",
        {"status": "in_transit", "location": "Memphis, TN"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_transit"
    assert len(body["tracking_events"]) == 2


def test_delivered_event_updates_order_items_and_delivered_at(
    api_client, customer, address, vendor, category
):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)
    created = api_client.post("/api/shipping/mine/", {"order": order.pk})
    shipment_id = created.json()["id"]

    response = api_client.post(f"/api/shipping/mine/{shipment_id}/events/", {"status": "delivered"})

    assert response.status_code == 200
    assert response.json()["delivered_at"] is not None
    item = OrderItem.objects.get(order=order, vendor=vendor)
    assert item.fulfillment_status == OrderItem.FulfillmentStatus.DELIVERED


def test_vendor_cannot_update_another_vendors_shipment(
    api_client, customer, address, vendor, pending_vendor, category
):
    from apps.vendors.models import VendorProfile

    pending_vendor.status = VendorProfile.Status.APPROVED
    pending_vendor.save(update_fields=["status"])

    order = _place_order(customer, address, pending_vendor, category)
    api_client.force_authenticate(user=pending_vendor.user)
    created = api_client.post("/api/shipping/mine/", {"order": order.pk})
    shipment_id = created.json()["id"]

    api_client.force_authenticate(user=vendor.user)
    response = api_client.post(f"/api/shipping/mine/{shipment_id}/events/", {"status": "in_transit"})

    assert response.status_code == 404


def test_customer_can_track_own_order(api_client, customer, address, vendor, category):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)
    api_client.post("/api/shipping/mine/", {"order": order.pk})

    api_client.force_authenticate(user=customer)
    response = api_client.get(f"/api/shipping/order/{order.pk}/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["vendor_store_name"] == vendor.store_name


def test_customer_cannot_track_another_users_order(
    api_client, customer, address, vendor, category, django_user_model
):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=vendor.user)
    api_client.post("/api/shipping/mine/", {"order": order.pk})

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    api_client.force_authenticate(user=other)
    response = api_client.get(f"/api/shipping/order/{order.pk}/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []
