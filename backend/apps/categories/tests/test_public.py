import pytest

from apps.categories.models import Category

pytestmark = pytest.mark.django_db


@pytest.fixture
def electronics():
    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def phones(electronics):
    return Category.objects.create(name="Phones", slug="phones", parent=electronics)


def test_list_categories_is_public(api_client, electronics, phones):
    response = api_client.get("/api/categories/")

    assert response.status_code == 200
    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 2


def test_list_filters_top_level_only(api_client, electronics, phones):
    response = api_client.get("/api/categories/?parent=null")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert [r["slug"] for r in results] == ["electronics"]


def test_list_filters_by_parent_id(api_client, electronics, phones):
    response = api_client.get(f"/api/categories/?parent={electronics.pk}")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert [r["slug"] for r in results] == ["phones"]


def test_detail_by_slug(api_client, phones):
    response = api_client.get("/api/categories/phones/")

    assert response.status_code == 200
    assert response.json()["name"] == "Phones"
