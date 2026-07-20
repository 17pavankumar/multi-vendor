import pytest
import razorpay

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.tests.conftest import place_order_with_payment

pytestmark = pytest.mark.django_db


def test_requires_authentication(api_client):
    response = api_client.post(
        "/api/payments/verify/",
        {
            "razorpay_order_id": "order_x",
            "razorpay_payment_id": "pay_x",
            "razorpay_signature": "sig_x",
        },
    )

    assert response.status_code == 401


def test_valid_signature_marks_payment_captured_and_order_paid(
    api_client, customer, address, vendor, category, mock_razorpay
):
    order, payment = place_order_with_payment(customer, address, vendor, category)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/payments/verify/",
        {
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "sig_test_123",
        },
    )

    assert response.status_code == 200
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.CAPTURED
    assert payment.razorpay_payment_id == "pay_test_123"
    assert payment.razorpay_signature == "sig_test_123"
    assert order.status == Order.Status.PAID


def test_invalid_signature_marks_payment_failed(
    api_client, customer, address, vendor, category, mock_razorpay
):
    order, payment = place_order_with_payment(customer, address, vendor, category)
    mock_razorpay.utility.verify_payment_signature.side_effect = razorpay.errors.SignatureVerificationError(
        "bad signature"
    )
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/payments/verify/",
        {
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "forged",
        },
    )

    assert response.status_code == 400
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.FAILED
    assert order.status == Order.Status.PENDING


def test_payment_scoped_to_owner(
    api_client, customer, address, vendor, category, mock_razorpay, django_user_model
):
    order, payment = place_order_with_payment(customer, address, vendor, category)

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    api_client.force_authenticate(user=other)

    response = api_client.post(
        "/api/payments/verify/",
        {
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "sig_test_123",
        },
    )

    assert response.status_code == 404


def test_unknown_razorpay_order_id_returns_404(api_client, customer, mock_razorpay):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/payments/verify/",
        {
            "razorpay_order_id": "order_does_not_exist",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "sig_test_123",
        },
    )

    assert response.status_code == 404
