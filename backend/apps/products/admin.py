from django.contrib import admin

from apps.products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "vendor", "category", "price", "status"]
    list_filter = ["status", "category"]
    search_fields = ["name", "sku", "slug"]
    inlines = [ProductImageInline]
