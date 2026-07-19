import pytest

from apps.users.models import User
from conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def test_register_creates_customer(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "bob@example.com",
            "password": TEST_PASSWORD,
            "first_name": "Bob",
            "last_name": "Builder",
        },
    )

    assert response.status_code == 201
    user = User.objects.get(email="bob@example.com")
    assert user.role == User.Role.CUSTOMER
    # Confirms the password went through UserManager's set_password(),
    # not stored as the plaintext that was posted.
    assert user.check_password(TEST_PASSWORD)
    assert user.password != TEST_PASSWORD


def test_register_ignores_posted_role(api_client):
    # `role` isn't a field on RegisterSerializer at all, so posting one
    # (even "admin") is silently dropped by DRF rather than rejected —
    # the account is still created, just always as a customer.
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "hacker@example.com",
            "password": TEST_PASSWORD,
            "first_name": "Bad",
            "last_name": "Actor",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    user = User.objects.get(email="hacker@example.com")
    assert user.role == User.Role.CUSTOMER


def test_register_rejects_weak_password(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "weak@example.com",
            "password": "password",
            "first_name": "Weak",
            "last_name": "Pass",
        },
    )

    assert response.status_code == 400


def test_register_rejects_duplicate_email(api_client, customer):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": customer.email,
            "password": TEST_PASSWORD,
            "first_name": "Dup",
            "last_name": "Licate",
        },
    )

    assert response.status_code == 400
