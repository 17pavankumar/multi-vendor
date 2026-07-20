import pytest

from apps.products.tests.conftest import make_product
from apps.reviews.models import Review
from apps.reviews.tests.conftest import place_delivered_order

pytestmark = pytest.mark.django_db


def test_create_requires_authentication(api_client):
    response = api_client.post("/api/reviews/", {"product": 1, "rating": 5})

    assert response.status_code == 401


def test_create_requires_delivered_purchase(api_client, customer, vendor, category):
    product = make_product(vendor, category)

    api_client.force_authenticate(user=customer)
    response = api_client.post("/api/reviews/", {"product": product.pk, "rating": 5})

    assert response.status_code == 400
    assert not Review.objects.exists()


def test_create_succeeds_for_delivered_purchase(api_client, customer, address, vendor, category):
    order, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/", {"product": product.pk, "rating": 5, "title": "Great!", "body": "Loved it."}
    )

    assert response.status_code == 201
    review = Review.objects.get(user=customer, product=product)
    assert review.order_item is not None
    assert review.order_item.order == order


def test_cannot_review_same_product_twice(api_client, customer, address, vendor, category):
    _, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)
    api_client.post("/api/reviews/", {"product": product.pk, "rating": 5})

    response = api_client.post("/api/reviews/", {"product": product.pk, "rating": 3})

    assert response.status_code == 400
    assert Review.objects.filter(user=customer, product=product).count() == 1


def test_rating_out_of_range_is_rejected(api_client, customer, address, vendor, category):
    _, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)

    response = api_client.post("/api/reviews/", {"product": product.pk, "rating": 6})

    assert response.status_code == 400
    assert not Review.objects.exists()


def test_product_review_list_is_public(api_client, customer, address, vendor, category):
    _, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)
    api_client.post("/api/reviews/", {"product": product.pk, "rating": 4, "title": "Good"})

    api_client.force_authenticate(user=None)
    response = api_client.get(f"/api/reviews/product/{product.pk}/")

    assert response.status_code == 200
    body = response.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 1
    assert results[0]["rating"] == 4


def test_delete_own_review(api_client, customer, address, vendor, category):
    _, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)
    created = api_client.post("/api/reviews/", {"product": product.pk, "rating": 5})
    review_id = created.json()["id"]

    response = api_client.delete(f"/api/reviews/{review_id}/")

    assert response.status_code == 204
    assert not Review.objects.filter(pk=review_id).exists()


def test_cannot_delete_another_users_review(
    api_client, customer, address, vendor, category, django_user_model
):
    _, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)
    created = api_client.post("/api/reviews/", {"product": product.pk, "rating": 5})
    review_id = created.json()["id"]

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    api_client.force_authenticate(user=other)
    response = api_client.delete(f"/api/reviews/{review_id}/")

    assert response.status_code == 404


def test_product_detail_shows_average_rating_and_count(api_client, customer, address, vendor, category):
    order, product = place_delivered_order(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)
    api_client.post("/api/reviews/", {"product": product.pk, "rating": 4})

    api_client.force_authenticate(user=None)
    response = api_client.get(f"/api/products/{product.slug}/")

    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.0
    assert response.json()["review_count"] == 1


def test_product_detail_rating_is_null_with_no_reviews(api_client, vendor, category):
    product = make_product(vendor, category)

    response = api_client.get(f"/api/products/{product.slug}/")

    assert response.json()["average_rating"] is None
    assert response.json()["review_count"] == 0
