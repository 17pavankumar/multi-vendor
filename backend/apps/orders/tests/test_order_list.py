import pytest

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
    response = api_client.get("/api/orders/")

    assert response.status_code == 401


def test_list_shows_only_own_orders(api_client, customer, address, vendor, category, django_user_model):
    _place_order(customer, address, vendor, category)

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    from apps.users.models import Address

    other_address = Address.objects.create(
        user=other, line1="10 Downing Street", city="London", state="London",
        postal_code="SW1A2AA", country="GB",
    )
    _place_order(other, other_address, vendor, category, name="Other", slug="other", sku="SKU-OTHER")

    api_client.force_authenticate(user=customer)
    response = api_client.get("/api/orders/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1


def test_detail_includes_items(api_client, customer, address, vendor, category):
    order = _place_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)

    response = api_client.get(f"/api/orders/{order.pk}/")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_cannot_view_another_users_order(api_client, customer, address, vendor, category, django_user_model):
    order = _place_order(customer, address, vendor, category)

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    api_client.force_authenticate(user=other)

    response = api_client.get(f"/api/orders/{order.pk}/")

    assert response.status_code == 404
