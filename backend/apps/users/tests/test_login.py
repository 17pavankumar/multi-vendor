import base64
import json

import pytest

from apps.users.tests.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def _decode_jwt_payload(token):
    payload_b64 = token.split(".")[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)  # restore stripped base64 padding
    return json.loads(base64.urlsafe_b64decode(payload_b64))


def test_login_returns_tokens_with_role_claim(api_client, customer):
    response = api_client.post("/api/auth/login/", {"email": customer.email, "password": TEST_PASSWORD})

    assert response.status_code == 200
    body = response.json()
    assert "access" in body and "refresh" in body

    payload = _decode_jwt_payload(body["access"])
    assert payload["role"] == "customer"
    assert payload["email"] == customer.email


def test_login_rejects_wrong_password(api_client, customer):
    response = api_client.post("/api/auth/login/", {"email": customer.email, "password": "wrong-password"})

    assert response.status_code == 401


def test_profile_requires_authentication(api_client):
    response = api_client.get("/api/auth/profile/")

    assert response.status_code == 401


def test_profile_returns_own_record_when_authenticated(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.get("/api/auth/profile/")

    assert response.status_code == 200
    assert response.json()["email"] == customer.email


def test_profile_cannot_change_own_role(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.patch("/api/auth/profile/", {"role": "admin"}, content_type="application/json")

    assert response.status_code == 200
    customer.refresh_from_db()
    # `role` is read-only on ProfileSerializer; a client sending it is
    # silently ignored rather than rejected.
    assert customer.role == "customer"
