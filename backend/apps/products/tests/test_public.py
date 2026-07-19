import pytest

from apps.products.models import Product
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_list_shows_active_products_from_approved_vendors(api_client, vendor, category):
    make_product(vendor, category)

    response = api_client.get("/api/products/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["name"] == "Wireless Mouse"


def test_list_hides_draft_products(api_client, vendor, category):
    make_product(vendor, category, status=Product.Status.DRAFT, slug="draft-product", sku="SKU-DRAFT")

    response = api_client.get("/api/products/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []


def test_list_hides_products_from_unapproved_vendors(api_client, pending_vendor, category):
    make_product(pending_vendor, category, slug="unapproved-product", sku="SKU-UNAPPROVED")

    response = api_client.get("/api/products/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []


def test_list_filters_by_price_range(api_client, vendor, category):
    make_product(vendor, category, name="Cheap", slug="cheap", sku="SKU-CHEAP", price="5.00")
    make_product(vendor, category, name="Pricey", slug="pricey", sku="SKU-PRICEY", price="500.00")

    response = api_client.get("/api/products/?min_price=100")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert [r["name"] for r in results] == ["Pricey"]


def test_list_search_matches_name(api_client, vendor, category):
    make_product(vendor, category, name="Wireless Mouse", slug="wireless-mouse", sku="SKU-1")
    make_product(vendor, category, name="USB Keyboard", slug="usb-keyboard", sku="SKU-2")

    response = api_client.get("/api/products/?search=mouse")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert [r["name"] for r in results] == ["Wireless Mouse"]


def test_detail_by_slug(api_client, vendor, category):
    make_product(vendor, category)

    response = api_client.get("/api/products/wireless-mouse/")

    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-MOUSE-1"


def test_detail_404s_for_draft_product(api_client, vendor, category):
    make_product(vendor, category, status=Product.Status.DRAFT)

    response = api_client.get("/api/products/wireless-mouse/")

    assert response.status_code == 404
