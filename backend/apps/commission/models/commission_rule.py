from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.categories.models import Category
from apps.vendors.models import VendorProfile


class CommissionRule(models.Model):
    """Overrides vendor_profiles.default_commission_rate for a specific
    vendor+category combination (e.g. the platform takes less
    commission on high-value electronics). vendor=None or category=None
    make a rule broader — see apps.commission.selectors.
    resolve_commission_rate for the exact resolution order applied at
    checkout."""

    vendor = models.ForeignKey(
        VendorProfile, null=True, blank=True, on_delete=models.CASCADE, related_name="commission_rules"
    )
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE, related_name="commission_rules"
    )
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "commission_rules"
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "category"], name="uq_commission_rules_vendor_category"
            ),
        ]

    def __str__(self):
        vendor_label = self.vendor.store_name if self.vendor else "any vendor"
        category_label = self.category.name if self.category else "any category"
        return f"{self.rate}% ({vendor_label} / {category_label})"
