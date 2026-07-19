from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    # Each feature app gets its own url include here as it's built —
    # e.g. path("api/products/", include("apps.products.urls")) in Phase 3.
]
