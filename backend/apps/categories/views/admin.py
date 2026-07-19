from rest_framework import viewsets

from apps.categories.models import Category
from apps.categories.serializers import CategoryWriteSerializer
from apps.users.permissions import IsAdminRole


class CategoryAdminViewSet(viewsets.ModelViewSet):
    """/api/categories/admin/ — full CRUD, admin only. Deliberately
    separate from the public list/detail views (views/public.py)
    instead of one ViewSet with permission-dependent serializers —
    keeps "what can the public see" and "what can an admin change"
    each in a single, easy-to-audit place."""

    permission_classes = [IsAdminRole]
    serializer_class = CategoryWriteSerializer
    queryset = Category.objects.all()
