import json

import pytest
import razorpay

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.tests.conftest import place_order_with_payment

pytestmark = pytest.mark.django_db


def _webhook_payload(event, razorpay_order_id, **entity_overrides):
    entity = {"id": "pay_test_123", "order_id": razorpay_order_id, "method": "upi"}
    entity.update(entity_overrides)
    return {"event": event, "payload": {"payment": {"entity": entity}}}


def test_no_authentication_required(api_client, customer, address, vendor, category, mock_razorpay):
    # The webhook is Razorpay's own server calling us, not a logged-in
    # user — no auth header is sent, only the signature header.
    order, payment = place_order_with_payment(customer, address, vendor, category)

    response = api_client.post(
        "/api/payments/webhook/",
        data=json.dumps(_webhook_payload("payment.captured", payment.razorpay_order_id)),
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE="valid-signature",
    )

    assert response.status_code == 200


def test_invalid_signature_is_rejected(api_client, customer, address, vendor, category, mock_razorpay):
    order, payment = place_order_with_payment(customer, address, vendor, category)
    mock_razorpay.utility.verify_webhook_signature.side_effect = razorpay.errors.SignatureVerificationError(
        "bad signature"
    )

    response = api_client.post(
        "/api/payments/webhook/",
        data=json.dumps(_webhook_payload("payment.captured", payment.razorpay_order_id)),
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE="forged",
    )

    assert response.status_code == 400
    payment.refresh_from_db()
    assert payment.status == Payment.Status.CREATED


def test_payment_captured_event_marks_order_paid(
    api_client, customer, address, vendor, category, mock_razorpay
):
    order, payment = place_order_with_payment(customer, address, vendor, category)

    response = api_client.post(
        "/api/payments/webhook/",
        data=json.dumps(_webhook_payload("payment.captured", payment.razorpay_order_id, method="card")),
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE="valid-signature",
    )

    assert response.status_code == 200
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.CAPTURED
    assert payment.method == "card"
    assert order.status == Order.Status.PAID


def test_payment_failed_event_marks_payment_failed(
    api_client, customer, address, vendor, category, mock_razorpay
):
    order, payment = place_order_with_payment(customer, address, vendor, category)

    response = api_client.post(
        "/api/payments/webhook/",
        data=json.dumps(
            _webhook_payload(
                "payment.failed",
                payment.razorpay_order_id,
                error_code="BAD_REQUEST_ERROR",
                error_description="Card declined",
            )
        ),
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE="valid-signature",
    )

    assert response.status_code == 200
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.FAILED
    assert payment.error_code == "BAD_REQUEST_ERROR"
    assert order.status == Order.Status.PENDING


def test_unknown_order_id_acks_without_error(api_client, mock_razorpay):
    response = api_client.post(
        "/api/payments/webhook/",
        data=json.dumps(_webhook_payload("payment.captured", "order_does_not_exist")),
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE="valid-signature",
    )

    assert response.status_code == 200
