from django.utils.text import slugify

from apps.vendors.models import VendorProfile


def generate_unique_store_slug(store_name: str) -> str:
    """Turns a store name into a URL slug, appending -2, -3, ... on
    collision so two vendors named "Acme Store" don't hit an
    IntegrityError on the unique store_slug column."""
    base_slug = slugify(store_name)[:150] or "store"
    slug = base_slug
    suffix = 2
    while VendorProfile.objects.filter(store_slug=slug).exists():
        slug = f"{base_slug}-{suffix}"[:160]
        suffix += 1
    return slug
