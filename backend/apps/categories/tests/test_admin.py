import pytest

from apps.categories.models import Category

pytestmark = pytest.mark.django_db


def test_create_requires_admin_role(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/categories/admin/", {"name": "Electronics"})

    assert response.status_code == 403
    assert not Category.objects.exists()


def test_admin_create_derives_slug_from_name(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post("/api/categories/admin/", {"name": "Home & Garden"})

    assert response.status_code == 201
    assert response.json()["slug"] == "home-garden"


def test_admin_update_without_slug_keeps_existing_slug(api_client, admin_user):
    category = Category.objects.create(name="Electronics", slug="electronics")
    api_client.force_authenticate(user=admin_user)

    response = api_client.patch(
        f"/api/categories/admin/{category.pk}/",
        {"name": "Consumer Electronics"},
        content_type="application/json",
    )

    assert response.status_code == 200
    category.refresh_from_db()
    assert category.slug == "electronics"
    assert category.name == "Consumer Electronics"


def test_admin_delete(api_client, admin_user):
    category = Category.objects.create(name="Electronics", slug="electronics")
    api_client.force_authenticate(user=admin_user)

    response = api_client.delete(f"/api/categories/admin/{category.pk}/")

    assert response.status_code == 204
    assert not Category.objects.filter(pk=category.pk).exists()
