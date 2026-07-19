import pytest

from apps.users.models import User
from apps.vendors.models import VendorProfile

pytestmark = pytest.mark.django_db


def test_apply_creates_pending_profile_and_flips_role(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/vendors/apply/",
        {"store_name": "Acme Store", "description": "We sell things"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    customer.refresh_from_db()
    assert customer.role == User.Role.VENDOR

    profile = VendorProfile.objects.get(user=customer)
    assert profile.store_slug == "acme-store"
    assert profile.status == VendorProfile.Status.PENDING


def test_apply_twice_is_rejected(api_client, customer):
    api_client.force_authenticate(user=customer)
    api_client.post("/api/vendors/apply/", {"store_name": "Acme Store"})

    response = api_client.post("/api/vendors/apply/", {"store_name": "Acme Store Again"})

    assert response.status_code == 400
    assert VendorProfile.objects.filter(user=customer).count() == 1


def test_apply_requires_authentication(api_client):
    response = api_client.post("/api/vendors/apply/", {"store_name": "Acme Store"})

    assert response.status_code == 401


def test_duplicate_store_name_gets_unique_slug(api_client, customer, django_user_model):
    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    VendorProfile.objects.create(user=other, store_name="Acme Store", store_slug="acme-store")

    api_client.force_authenticate(user=customer)
    response = api_client.post("/api/vendors/apply/", {"store_name": "Acme Store"})

    assert response.status_code == 201
    profile = VendorProfile.objects.get(user=customer)
    assert profile.store_slug == "acme-store-2"
