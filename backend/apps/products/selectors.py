from apps.products.models import Product


def visible_products():
    """Only products that are both live (status=active) AND belong to
    an approved vendor — the single definition of "publicly purchasable"
    shared by product browsing (views/public.py) and anything that adds
    a product to a cart or wishlist (apps.cart, apps.wishlist), so the
    rule can't drift between "what shows up when browsing" and "what
    can actually be bought"."""
    return Product.objects.filter(status=Product.Status.ACTIVE, vendor__status="approved").select_related(
        "vendor", "category"
    )
