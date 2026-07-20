import pytest

from apps.products.models import Product
from apps.products.tests.conftest import make_product
from apps.wishlist.models import WishlistItem

pytestmark = pytest.mark.django_db


def test_requires_authentication(api_client):
    response = api_client.get("/api/wishlist/")

    assert response.status_code == 401


def test_add_and_list(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)

    add_response = api_client.post("/api/wishlist/", {"product": product.pk})
    list_response = api_client.get("/api/wishlist/")

    assert add_response.status_code == 201
    body = list_response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["product_name"] == "Wireless Mouse"


def test_duplicate_add_is_rejected(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)
    api_client.post("/api/wishlist/", {"product": product.pk})

    response = api_client.post("/api/wishlist/", {"product": product.pk})

    assert response.status_code == 400
    assert WishlistItem.objects.filter(user=customer, product=product).count() == 1


def test_cannot_wishlist_draft_product(api_client, customer, vendor, category):
    product = make_product(vendor, category, status=Product.Status.DRAFT)
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/wishlist/", {"product": product.pk})

    assert response.status_code == 400


def test_delete_item(api_client, customer, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=customer)
    created = api_client.post("/api/wishlist/", {"product": product.pk})
    item_id = created.json()["id"]

    response = api_client.delete(f"/api/wishlist/{item_id}/")

    assert response.status_code == 204
    assert not WishlistItem.objects.filter(pk=item_id).exists()


def test_wishlist_scoped_to_owner(api_client, customer, vendor, category, django_user_model):
    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    product = make_product(vendor, category)
    WishlistItem.objects.create(user=other, product=product)

    api_client.force_authenticate(user=customer)
    response = api_client.get("/api/wishlist/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []
