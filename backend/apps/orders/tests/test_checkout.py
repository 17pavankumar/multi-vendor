import pytest
import razorpay

from apps.cart.models import CartItem
from apps.coupons.models import Coupon
from apps.orders.models import CouponRedemption, Order, OrderItem
from apps.orders.tests.conftest import add_to_cart
from apps.payments.models import Payment
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def _stock(product, quantity):
    product.inventory.quantity = quantity
    product.inventory.save(update_fields=["quantity"])


def test_checkout_requires_authentication(api_client):
    response = api_client.post("/api/orders/checkout/", {"shipping_address_id": 1, "billing_address_id": 1})

    assert response.status_code == 401


def test_empty_cart_is_rejected(api_client, customer, address, mock_razorpay):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_invalid_address_is_rejected(api_client, customer, vendor, category, mock_razorpay):
    product = make_product(vendor, category)
    _stock(product, 10)
    add_to_cart(customer, product)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/", {"shipping_address_id": 999999, "billing_address_id": 999999}
    )

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_insufficient_stock_is_rejected(api_client, customer, address, vendor, category, mock_razorpay):
    product = make_product(vendor, category)
    _stock(product, 1)
    add_to_cart(customer, product, quantity=5)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_successful_checkout(api_client, customer, address, vendor, category, mock_razorpay):
    product = make_product(vendor, category, price="20.00")
    _stock(product, 10)
    add_to_cart(customer, product, quantity=2)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["order"]["status"] == "pending"
    assert body["order"]["subtotal"] == "40.00"
    assert body["order"]["total_amount"] == "40.00"
    assert body["razorpay_order_id"] == "order_test_razorpay_123"

    order = Order.objects.get(user=customer)
    assert order.items.count() == 1
    item = order.items.first()
    assert item.vendor_id == vendor.pk
    assert item.quantity == 2
    assert item.commission_rate == vendor.default_commission_rate

    product.inventory.refresh_from_db()
    assert product.inventory.reserved_quantity == 2

    assert CartItem.objects.filter(cart__user=customer).count() == 0
    assert Payment.objects.filter(order=order, razorpay_order_id="order_test_razorpay_123").exists()


def test_checkout_splits_across_vendors(
    api_client, customer, address, vendor, pending_vendor, category, mock_razorpay
):
    # pending_vendor here is just a second, distinct VendorProfile — its
    # approval status doesn't matter for checkout (only for whether the
    # product was visible/addable to the cart in the first place).
    from apps.vendors.models import VendorProfile

    pending_vendor.status = VendorProfile.Status.APPROVED
    pending_vendor.save(update_fields=["status"])

    product_a = make_product(vendor, category, name="A", slug="a", sku="SKU-A", price="10.00")
    product_b = make_product(pending_vendor, category, name="B", slug="b", sku="SKU-B", price="15.00")
    _stock(product_a, 10)
    _stock(product_b, 10)
    add_to_cart(customer, product_a, quantity=1)
    add_to_cart(customer, product_b, quantity=1)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    assert response.status_code == 201
    order = Order.objects.get(user=customer)
    assert order.items.count() == 2
    vendors_on_order = set(order.items.values_list("vendor_id", flat=True))
    assert vendors_on_order == {vendor.pk, pending_vendor.pk}


def test_checkout_with_valid_coupon(api_client, customer, address, vendor, category, mock_razorpay):
    from datetime import timedelta

    from django.utils import timezone

    coupon = Coupon.objects.create(
        code="SAVE10",
        discount_type=Coupon.DiscountType.PERCENT,
        discount_value="10.00",
        valid_from=timezone.now() - timedelta(days=1),
        valid_until=timezone.now() + timedelta(days=1),
    )
    product = make_product(vendor, category, price="100.00")
    _stock(product, 10)
    add_to_cart(customer, product, quantity=1)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {
            "shipping_address_id": address.pk,
            "billing_address_id": address.pk,
            "coupon_code": "save10",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["order"]["discount_amount"] == "10.00"
    assert body["order"]["total_amount"] == "90.00"

    order = Order.objects.get(user=customer)
    redemption = CouponRedemption.objects.get(order=order)
    assert redemption.coupon == coupon
    assert redemption.discount_amount == 10

    coupon.refresh_from_db()
    assert coupon.usage_count == 1


def test_checkout_with_invalid_coupon_code(api_client, customer, address, vendor, category, mock_razorpay):
    product = make_product(vendor, category)
    _stock(product, 10)
    add_to_cart(customer, product)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {
            "shipping_address_id": address.pk,
            "billing_address_id": address.pk,
            "coupon_code": "NOPE",
        },
    )

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_checkout_uses_own_address_only(
    api_client, customer, vendor, category, mock_razorpay, django_user_model
):
    from apps.users.models import Address

    other = django_user_model.objects.create_user(
        email="other@example.com", password="S0meStr0ngPass!", first_name="Other", last_name="User"
    )
    other_address = Address.objects.create(
        user=other, line1="10 Downing Street", city="London", state="London",
        postal_code="SW1A2AA", country="GB",
    )
    product = make_product(vendor, category)
    _stock(product, 10)
    add_to_cart(customer, product)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": other_address.pk, "billing_address_id": other_address.pk},
    )

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_order_items_default_pending_fulfillment(
    api_client, customer, address, vendor, category, mock_razorpay
):
    product = make_product(vendor, category)
    _stock(product, 10)
    add_to_cart(customer, product)
    api_client.force_authenticate(user=customer)

    api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    item = OrderItem.objects.get(order__user=customer)
    assert item.fulfillment_status == OrderItem.FulfillmentStatus.PENDING


def test_checkout_rolls_back_order_when_razorpay_rejects_the_request(
    api_client, customer, address, vendor, category, mock_razorpay
):
    # Reproduces what actually happened testing this in a browser
    # against placeholder Razorpay credentials: create_payment_for_order()
    # raises after checkout() already committed an order with reserved
    # stock. The whole request must roll back together, not leave that
    # order and reservation stranded with a 500 and no way to pay.
    mock_razorpay.order.create.side_effect = razorpay.errors.BadRequestError("invalid api key")
    product = make_product(vendor, category)
    _stock(product, 10)
    add_to_cart(customer, product)
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/orders/checkout/",
        {"shipping_address_id": address.pk, "billing_address_id": address.pk},
    )

    assert response.status_code == 502
    assert not Order.objects.exists()
    assert not Payment.objects.exists()
    assert CartItem.objects.filter(cart__user=customer).count() == 1
    product.inventory.refresh_from_db()
    assert product.inventory.reserved_quantity == 0
