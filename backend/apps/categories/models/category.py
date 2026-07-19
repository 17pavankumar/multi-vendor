from django.db import models


class Category(models.Model):
    """Self-referencing tree (Electronics -> Phones). parent=None means
    a top-level category."""

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
