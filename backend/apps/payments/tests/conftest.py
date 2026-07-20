from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.payments.services import create_payment_for_order
from apps.products.tests.conftest import make_product


def place_order_with_payment(customer, address, vendor, category, **product_overrides):
    """Requires the `mock_razorpay` fixture to already be active in the
    calling test — create_payment_for_order() calls out to it."""
    product = make_product(vendor, category, **product_overrides)
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    order = do_checkout(customer, address)
    payment = create_payment_for_order(order)
    return order, payment
