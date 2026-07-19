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
