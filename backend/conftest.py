"""
Root-level fixtures, available to every test in backend/apps/*/tests/
without an import — pytest auto-discovers conftest.py files up the
directory tree. App-specific conftest.py files (if any) can add
fixtures local to that app on top of these.
"""

import pytest
from rest_framework.test import APIClient

TEST_PASSWORD = "S0meStr0ngPass!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(django_user_model):
    return django_user_model.objects.create_user(
        email="alice@example.com",
        password=TEST_PASSWORD,
        first_name="Alice",
        last_name="Doe",
    )


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(
        email="admin@example.com",
        password=TEST_PASSWORD,
        first_name="Ada",
        last_name="Admin",
    )


@pytest.fixture
def vendor(django_user_model):
    """An approved vendor with a VendorProfile already attached — the
    common case most products/inventory tests need, so they don't have
    to replay the apply-then-approve flow themselves."""
    from apps.vendors.models import VendorProfile

    user = django_user_model.objects.create_user(
        email="vera@example.com",
        password=TEST_PASSWORD,
        first_name="Vera",
        last_name="Vendor",
        role=django_user_model.Role.VENDOR,
    )
    return VendorProfile.objects.create(
        user=user,
        store_name="Vera's Store",
        store_slug="veras-store",
        status=VendorProfile.Status.APPROVED,
    )


@pytest.fixture
def category():
    from apps.categories.models import Category

    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def pending_vendor(django_user_model):
    """A vendor whose application hasn't been approved yet — used to
    confirm their products never appear on the public storefront and
    that other vendors can't see their data."""
    from apps.vendors.models import VendorProfile

    user = django_user_model.objects.create_user(
        email="penny@example.com",
        password=TEST_PASSWORD,
        first_name="Penny",
        last_name="Pending",
        role=django_user_model.Role.VENDOR,
    )
    return VendorProfile.objects.create(user=user, store_name="Pending Store", store_slug="pending-store")
