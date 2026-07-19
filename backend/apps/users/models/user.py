from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    One table for every human in the system — customer, vendor, or
    admin — distinguished by `role`. They share every login/auth field,
    so splitting them into separate tables would just mean duplicating
    this whole model three times. A vendor is a User who *also* owns a
    VendorProfile row (see apps/vendors); an admin is just a User with
    role="admin" and is_staff=True for Django admin-site access.
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        VENDOR = "vendor", "Vendor"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    # is_staff controls access to Django's /admin/ site — separate from
    # `role`, which controls access to our own API. An "admin" role user
    # is also given is_staff=True (see managers.create_superuser and the
    # approval flow), but the two flags answer different questions.
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def is_vendor(self):
        return self.role == self.Role.VENDOR

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER
