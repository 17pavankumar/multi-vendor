from rest_framework.permissions import BasePermission

from apps.users.models import User


def _has_role(request, role):
    return bool(request.user and request.user.is_authenticated and request.user.role == role)


class IsCustomer(BasePermission):
    """Grants access only to authenticated users with role="customer" —
    used on cart/wishlist/checkout endpoints vendors and admins shouldn't hit."""

    def has_permission(self, request, view):
        return _has_role(request, User.Role.CUSTOMER)


class IsVendor(BasePermission):
    """Grants access only to authenticated users with role="vendor" —
    used on product-management, inventory, and vendor-analytics endpoints."""

    def has_permission(self, request, view):
        return _has_role(request, User.Role.VENDOR)


class IsAdminRole(BasePermission):
    """Grants access only to authenticated users with role="admin" —
    used on vendor-approval, commission, and platform-report endpoints."""

    def has_permission(self, request, view):
        return _has_role(request, User.Role.ADMIN)
