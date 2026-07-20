import pytest

from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_cart_requires_authentication(api_client):
    response = api_client.get("/api/cart/")

    assert response.status_code == 401


def test_get_cart_creates_one_lazily(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.get("/api/cart/")

    assert response.status_code == 200
    assert Cart.objects.filter(user=customer).exists()
    assert response.json()["items"] == []
    assert response.json()["subtotal"] == "0.00"


def test_add_item_snapshots_price(api_client, customer, vendor, category):
    product = make_product(vendor, category, price="19.99")
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 2})

    assert response.status_code == 201
    assert response.json()["unit_price"] == "19.99"
    item = CartItem.objects.get(cart__user=customer, product=product)
    assert item.quantity == 2
    assert item.line_total == 39.98 or str(item.line_total) == "39.98"


def test_adding_same_product_twice_increases_quantity(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)

    api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})
    api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 2})

    item = CartItem.objects.get(cart__user=customer, product=product)
    assert item.quantity == 3
    assert CartItem.objects.filter(cart__user=customer).count() == 1


def test_cannot_add_draft_product(api_client, customer, vendor, category):
    product = make_product(vendor, category, status=Product.Status.DRAFT)
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})

    assert response.status_code == 400


def test_cannot_add_product_from_unapproved_vendor(api_client, customer, pending_vendor, category):
    product = make_product(pending_vendor, category, slug="unapproved", sku="SKU-UNAPPROVED")
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})

    assert response.status_code == 400


def test_update_quantity(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)
    created = api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})
    item_id = created.json()["id"]

    response = api_client.patch(
        f"/api/cart/items/{item_id}/", {"quantity": 5}, content_type="application/json"
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_delete_item(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)
    created = api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})
    item_id = created.json()["id"]

    response = api_client.delete(f"/api/cart/items/{item_id}/")

    assert response.status_code == 204
    assert not CartItem.objects.filter(pk=item_id).exists()


def test_clear_cart(api_client, customer, vendor, category):
    make_product(vendor, category, slug="p1", sku="SKU-1")
    make_product(vendor, category, name="Second", slug="p2", sku="SKU-2")
    api_client.force_authenticate(user=customer)
    for product in Product.objects.all():
        api_client.post("/api/cart/items/", {"product": product.pk, "quantity": 1})
    assert CartItem.objects.filter(cart__user=customer).count() == 2

    response = api_client.delete("/api/cart/clear/")

    assert response.status_code == 204
    assert CartItem.objects.filter(cart__user=customer).count() == 0


def test_cart_items_are_scoped_to_owner(api_client, customer, vendor, category, django_user_model):
    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    other_cart = Cart.objects.create(user=other)
    product = make_product(vendor, category)
    CartItem.objects.create(cart=other_cart, product=product, quantity=1, unit_price=product.price)

    api_client.force_authenticate(user=customer)
    response = api_client.get("/api/cart/items/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []


def test_subtotal_sums_line_totals(api_client, customer, vendor, category):
    p1 = make_product(vendor, category, name="A", slug="a", sku="SKU-A", price="10.00")
    p2 = make_product(vendor, category, name="B", slug="b", sku="SKU-B", price="5.00")
    api_client.force_authenticate(user=customer)
    api_client.post("/api/cart/items/", {"product": p1.pk, "quantity": 2})
    api_client.post("/api/cart/items/", {"product": p2.pk, "quantity": 3})

    response = api_client.get("/api/cart/")

    assert response.json()["subtotal"] == "35.00"
