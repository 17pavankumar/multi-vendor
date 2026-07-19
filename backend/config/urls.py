from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/vendors/", include("apps.vendors.urls")),
    path("api/categories/", include("apps.categories.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
]

if settings.DEBUG:
    # Serves uploaded product images from MEDIA_ROOT in local dev only —
    # in production this is nginx's/the storage backend's job, never Django's.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
