import pytest

pytestmark = pytest.mark.django_db


def test_profile_requires_authentication(api_client):
    response = api_client.get("/api/vendors/profile/")

    assert response.status_code == 401


def test_profile_404s_for_user_without_vendor_profile(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.get("/api/vendors/profile/")

    assert response.status_code == 404


def test_profile_returns_own_store(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.get("/api/vendors/profile/")

    assert response.status_code == 200
    assert response.json()["store_name"] == "Vera's Store"


def test_profile_update_cannot_change_status_or_slug(api_client, vendor):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.patch(
        "/api/vendors/profile/",
        {"status": "suspended", "store_slug": "hijacked-slug", "description": "Updated bio"},
        content_type="application/json",
    )

    assert response.status_code == 200
    vendor.refresh_from_db()
    assert vendor.status == "approved"  # unchanged — status is read-only here
    assert vendor.store_slug == "veras-store"  # unchanged — slug is read-only here
    assert vendor.description == "Updated bio"  # this field IS writable
