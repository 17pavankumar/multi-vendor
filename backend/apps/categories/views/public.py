from rest_framework import generics, permissions

from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ — the whole flat list (small, curated table;
    no pagination concerns). ?parent=<id> narrows to that category's
    direct children, ?parent=null (or empty) narrows to top-level ones."""

    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        if "parent" in self.request.query_params:
            parent_param = self.request.query_params["parent"]
            if parent_param in ("", "null"):
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_param)
        return queryset


class CategoryDetailView(generics.RetrieveAPIView):
    """GET /api/categories/<slug>/"""

    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "slug"
