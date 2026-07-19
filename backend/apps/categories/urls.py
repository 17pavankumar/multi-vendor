from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.categories.views import CategoryAdminViewSet, CategoryDetailView, CategoryListView

router = SimpleRouter()
router.register("admin", CategoryAdminViewSet, basename="category-admin")

urlpatterns = [
    # SimpleRouter, not DefaultRouter: DefaultRouter auto-generates a
    # browsable-API root view mounted at the router's own "" path, which
    # would shadow CategoryListView below (both registered at "") and
    # silently require auth on it (the root view uses the project's
    # default IsAuthenticated permission, not CategoryListView's
    # AllowAny) — caught by test_list_categories_is_public unexpectedly
    # getting a 401. SimpleRouter has no such root view.
    #
    # Ordering still matters here independent of that: router (admin/...)
    # must be matched before the <slug:slug>/ catch-all below — "admin"
    # is itself a valid slug, so the wrong order would route
    # GET /api/categories/admin/ into CategoryDetailView(slug="admin")
    # instead of the admin viewset.
    path("", include(router.urls)),
    path("", CategoryListView.as_view(), name="category-list"),
    path("<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
]
