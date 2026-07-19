from django.utils.text import slugify
from rest_framework import serializers

from apps.categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Public read serializer — browsing the category tree."""

    class Meta:
        model = Category
        fields = ["id", "parent", "name", "slug", "image_url", "created_at"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    """Admin-only create/update. `slug` is optional on input — left
    blank, it's derived from `name`, matching the vendor store_slug
    pattern (see apps.vendors.utils.generate_unique_store_slug), but
    categories are few and curated, so a plain slugify() without a
    collision-suffix loop is enough: a duplicate just raises the
    model's normal uniqueness error instead of silently renaming."""

    class Meta:
        model = Category
        fields = ["id", "parent", "name", "slug", "image_url"]
        extra_kwargs = {"slug": {"required": False}}

    def validate(self, attrs):
        # Only derive a slug when creating (self.instance is None) and
        # none was given — on an update with no slug in the request,
        # `attrs` simply won't have a "slug" key at all, so leaving this
        # branch alone means the existing slug is untouched rather than
        # regenerated from a possibly-unrelated name change.
        if not attrs.get("slug") and self.instance is None:
            attrs["slug"] = slugify(attrs["name"])
        return attrs
