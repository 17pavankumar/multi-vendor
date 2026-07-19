from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import Address, User


class UserAdmin(DjangoUserAdmin):
    """Reuses Django's battle-tested UserAdmin (password change form,
    permission widgets, etc.) but repoints every field group at our
    email-based model instead of the default username-based one."""

    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "role", "is_active", "is_staff"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active", "is_staff", "is_superuser",
                    "is_verified", "groups", "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "first_name", "last_name"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Address)
