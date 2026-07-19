from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventory.models import Inventory
from apps.products.models import Product


@receiver(post_save, sender=Product)
def create_inventory_for_new_product(sender, instance, created, **kwargs):
    """Every product needs exactly one inventory row from the moment it
    exists. Creating it here — rather than requiring every code path
    that creates a Product to remember to also create an Inventory —
    means it's impossible to end up with a product that has none."""
    if created:
        Inventory.objects.get_or_create(product=instance)
