import pytest

from apps.vendors.models import VendorProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def pending_profile(customer):
    return VendorProfile.objects.create(user=customer, store_name="Pending Store", store_slug="pending-store")


def test_admin_list_requires_admin_role(api_client, customer, pending_profile):
    api_client.force_authenticate(user=customer)

    response = api_client.get("/api/vendors/admin/")

    assert response.status_code == 403


def test_admin_list_returns_all_profiles(api_client, admin_user, pending_profile, vendor):
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/vendors/admin/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert response.status_code == 200
    assert len(results) == 2


def test_admin_list_filters_by_status(api_client, admin_user, pending_profile, vendor):
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/vendors/admin/?status=pending")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["store_name"] == "Pending Store"


def test_admin_approve_sets_status_and_decision_metadata(api_client, admin_user, pending_profile):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(f"/api/vendors/admin/{pending_profile.pk}/approve/")

    assert response.status_code == 200
    pending_profile.refresh_from_db()
    assert pending_profile.status == VendorProfile.Status.APPROVED
    assert pending_profile.approved_by == admin_user
    assert pending_profile.approved_at is not None


def test_admin_reject_sets_status(api_client, admin_user, pending_profile):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(f"/api/vendors/admin/{pending_profile.pk}/reject/")

    assert response.status_code == 200
    pending_profile.refresh_from_db()
    assert pending_profile.status == VendorProfile.Status.REJECTED


def test_approve_requires_admin_role(api_client, vendor, pending_profile):
    api_client.force_authenticate(user=vendor.user)

    response = api_client.post(f"/api/vendors/admin/{pending_profile.pk}/approve/")

    assert response.status_code == 403
