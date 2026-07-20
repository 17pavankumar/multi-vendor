from apps.orders.models import OrderItem
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product


def place_delivered_order(customer, address, vendor, category, **product_overrides):
    """Places an order and marks it delivered directly (bypassing the
    shipping flow, which is tested separately) — reviews only care that
    a delivered OrderItem exists."""
    product = make_product(vendor, category, **product_overrides)
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    order = do_checkout(customer, address)
    OrderItem.objects.filter(order=order).update(fulfillment_status=OrderItem.FulfillmentStatus.DELIVERED)
    return order, product
