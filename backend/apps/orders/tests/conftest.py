from apps.cart.models import Cart, CartItem
from apps.orders.services import checkout


def add_to_cart(user, product, quantity=1):
    cart, _ = Cart.objects.get_or_create(user=user)
    return CartItem.objects.create(
        cart=cart, product=product, quantity=quantity, unit_price=product.effective_price
    )


def do_checkout(user, address, coupon_code=None):
    """Calls the checkout service directly, bypassing HTTP and Razorpay
    entirely — for tests (order list, vendor sales) that just need an
    existing Order to already exist, not to exercise checkout itself."""
    return checkout(
        user=user,
        shipping_address_id=address.pk,
        billing_address_id=address.pk,
        coupon_code=coupon_code,
    )
