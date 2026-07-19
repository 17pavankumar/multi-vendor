from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import AddressViewSet, ProfileView, RegisterView, RoleTokenObtainPairView

# SimpleRouter, not DefaultRouter — DefaultRouter mounts an
# auto-generated browsable-API root view at the router's own "" path,
# which would otherwise sit at GET /api/auth/ requiring auth by
# default. See apps/categories/urls.py for the full story (a real
# routing bug this exact pattern caused there).
router = SimpleRouter()
router.register("addresses", AddressViewSet, basename="address")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", RoleTokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", include(router.urls)),
]
