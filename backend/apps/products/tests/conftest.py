from apps.products.models import Product


def make_product(vendor, category, **overrides):
    defaults = {
        "vendor": vendor,
        "category": category,
        "name": "Wireless Mouse",
        "slug": "wireless-mouse",
        "price": "19.99",
        "sku": "SKU-MOUSE-1",
        "status": Product.Status.ACTIVE,
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)
