from django.db import models

from apps.products.models.product import Product


class ProductImage(models.Model):
    """`image` is a real file upload (Pillow-validated), not a pasted
    URL — stored under MEDIA_ROOT/products/ and served from MEDIA_URL.
    db_column keeps the underlying column named image_url, matching
    db/schema.sql; "image_url" is also the name the API exposes it
    under (see serializers/image.py) — `image` is purely the Django-
    internal field name.

    "At most one primary image per product" is enforced at the
    application layer (serializers/image.py), not a DB constraint — see
    db/schema.sql's comment on this table for why a generated-column
    version of this was tried and reverted."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", max_length=500, db_column="image_url")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "product_images"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} image #{self.pk}"
