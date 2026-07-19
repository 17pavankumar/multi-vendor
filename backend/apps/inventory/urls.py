from rest_framework.routers import SimpleRouter

from apps.inventory.views import VendorInventoryViewSet

# SimpleRouter, not DefaultRouter — see the note in apps/categories/urls.py
# for why DefaultRouter's auto-root view is avoided project-wide here.
router = SimpleRouter()
router.register("mine", VendorInventoryViewSet, basename="inventory-mine")

urlpatterns = router.urls
