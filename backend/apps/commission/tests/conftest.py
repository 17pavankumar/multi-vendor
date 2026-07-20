from apps.orders.models import Order, OrderItem
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product


def place_delivered_order_on_date(customer, address, vendor, category, placed_date, **product_overrides):
    """Places and delivers an order, then backdates it to `placed_date`
    (a datetime) — Order.placed_at is auto_now_add, so it can't be set
    on create(); .update() bypasses that."""
    product = make_product(vendor, category, **product_overrides)
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)
    order = do_checkout(customer, address)
    OrderItem.objects.filter(order=order).update(fulfillment_status=OrderItem.FulfillmentStatus.DELIVERED)
    Order.objects.filter(pk=order.pk).update(placed_at=placed_date)
    order.refresh_from_db()
    return order
