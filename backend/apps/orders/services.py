from decimal import Decimal

from django.db import transaction

from apps.cart.models import Cart
from apps.coupons.models import Coupon
from apps.inventory.models import Inventory
from apps.orders.models import CouponRedemption, Order, OrderItem
from apps.users.models import Address


class CheckoutError(Exception):
    """Raised for any checkout-time validation failure (empty cart,
    invalid address, insufficient stock, inapplicable coupon) — the
    view (views/checkout.py) turns this into a 400 with the message
    as-is; nothing here talks HTTP."""


@transaction.atomic
def checkout(user, shipping_address_id, billing_address_id, coupon_code=None):
    """Turns the user's cart into an Order. Everything happens in one
    transaction: if anything fails partway (a race on stock, a bad
    coupon), nothing is left half-created — no orphaned Order with no
    items, no reserved stock with no matching order."""
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = list(cart.items.select_related("product", "product__vendor").all())
    if not cart_items:
        raise CheckoutError("Your cart is empty.")

    try:
        shipping_address = Address.objects.get(pk=shipping_address_id, user=user)
        billing_address = Address.objects.get(pk=billing_address_id, user=user)
    except Address.DoesNotExist as exc:
        raise CheckoutError("Invalid shipping or billing address.") from exc

    # select_for_update locks each product's inventory row for the rest
    # of this transaction, so two customers checking out the last unit
    # of the same product at the same moment can't both succeed.
    reservations = []
    subtotal = Decimal("0.00")
    for cart_item in cart_items:
        inventory = Inventory.objects.select_for_update().get(product=cart_item.product)
        if inventory.available_quantity < cart_item.quantity:
            raise CheckoutError(f'Not enough stock for "{cart_item.product.name}".')
        line_subtotal = cart_item.unit_price * cart_item.quantity
        subtotal += line_subtotal
        reservations.append((cart_item, inventory, line_subtotal))

    coupon = None
    discount_amount = Decimal("0.00")
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
        except Coupon.DoesNotExist as exc:
            raise CheckoutError("Coupon not found.") from exc
        computed_discount = coupon.compute_discount(subtotal)
        if computed_discount is None:
            raise CheckoutError("This coupon isn't applicable.")
        discount_amount = computed_discount

    shipping_amount = Decimal("0.00")
    tax_amount = Decimal("0.00")
    total_amount = subtotal - discount_amount + shipping_amount + tax_amount

    order = Order.objects.create(
        user=user,
        subtotal=subtotal,
        discount_amount=discount_amount,
        shipping_amount=shipping_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        shipping_address=shipping_address,
        billing_address=billing_address,
    )

    for cart_item, inventory, line_subtotal in reservations:
        vendor = cart_item.product.vendor
        # Category/vendor-specific commission overrides (schema.sql's
        # commission_rules table) belong to a later admin-facing phase
        # — for now every item uses the vendor's own default rate.
        commission_rate = vendor.default_commission_rate
        commission_amount = (line_subtotal * commission_rate / Decimal("100")).quantize(Decimal("0.01"))
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            vendor=vendor,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            subtotal=line_subtotal,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
        )
        inventory.reserved_quantity += cart_item.quantity
        inventory.save(update_fields=["reserved_quantity"])

    if coupon is not None:
        CouponRedemption.objects.create(
            coupon=coupon, order=order, user=user, discount_amount=discount_amount
        )
        coupon.usage_count += 1
        coupon.save(update_fields=["usage_count"])

    cart.items.all().delete()

    return order
