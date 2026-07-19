import pytest

from apps.products.models import Product
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_create_requires_authentication(api_client, category):
    response = api_client.post(
        "/api/products/mine/",
        {"category": category.pk, "name": "New Product", "price": "9.99", "sku": "SKU-NEW"},
    )

    assert response.status_code == 401


def test_create_requires_vendor_profile(api_client, customer, category):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/products/mine/",
        {"category": category.pk, "name": "New Product", "price": "9.99", "sku": "SKU-NEW"},
    )

    assert response.status_code == 403


def test_vendor_can_create_product_and_gets_slug(api_client, vendor, category):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(
        "/api/products/mine/",
        {"category": category.pk, "name": "New Product", "price": "9.99", "sku": "SKU-NEW"},
    )

    assert response.status_code == 201
    assert response.json()["slug"] == "new-product"
    assert response.json()["status"] == "draft"
    product = Product.objects.get(sku="SKU-NEW")
    assert product.vendor_id == vendor.pk


def test_vendor_cannot_set_discount_above_price(api_client, vendor, category):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(
        "/api/products/mine/",
        {
            "category": category.pk,
            "name": "New Product",
            "price": "9.99",
            "discount_price": "19.99",
            "sku": "SKU-NEW",
        },
    )

    assert response.status_code == 400


def test_vendor_list_includes_own_drafts(api_client, vendor, category):
    make_product(vendor, category, status=Product.Status.DRAFT)
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/products/mine/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1


def test_vendor_cannot_see_or_edit_another_vendors_product(api_client, vendor, pending_vendor, category):
    other_product = make_product(pending_vendor, category, slug="other-product", sku="SKU-OTHER")
    api_client.force_authenticate(user=vendor.user)

    list_response = api_client.get("/api/products/mine/")
    body = list_response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []

    edit_response = api_client.patch(
        f"/api/products/mine/{other_product.pk}/",
        {"name": "Hijacked"},
        content_type="application/json",
    )
    assert edit_response.status_code == 404
