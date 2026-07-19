import pytest

from apps.users.models import Address
from apps.users.tests.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def _address_payload(**overrides):
    payload = {
        "label": "Home",
        "line1": "221B Baker Street",
        "city": "London",
        "state": "London",
        "postal_code": "NW16XE",
        "country": "GB",
        "is_default": True,
    }
    payload.update(overrides)
    return payload


def test_create_address(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/auth/addresses/", _address_payload())

    assert response.status_code == 201
    assert Address.objects.filter(user=customer, city="London").exists()


def test_second_default_address_unsets_first(api_client, customer):
    api_client.force_authenticate(user=customer)

    api_client.post("/api/auth/addresses/", _address_payload(label="Home"))
    api_client.post("/api/auth/addresses/", _address_payload(label="Office", line1="10 Downing Street"))

    defaults = Address.objects.filter(user=customer, is_default=True)
    assert defaults.count() == 1
    assert defaults.first().label == "Office"


def test_addresses_are_scoped_to_owner(api_client, customer, django_user_model):
    other = django_user_model.objects.create_user(
        email="other@example.com", password=TEST_PASSWORD, first_name="Other", last_name="User"
    )
    Address.objects.create(user=other, **_address_payload())

    api_client.force_authenticate(user=customer)
    response = api_client.get("/api/auth/addresses/")

    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results == []  # `customer` must not see `other`'s address


def test_addresses_require_authentication(api_client):
    response = api_client.get("/api/auth/addresses/")

    assert response.status_code == 401
