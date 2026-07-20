from apps.commission.models import CommissionRule


def resolve_commission_rate(vendor, category):
    """Resolution order: an exact vendor+category rule, then a
    category-wide rule (vendor=None), then the vendor's own default
    rate — never a platform-wide flat fallback, since a vendor's
    default_commission_rate always exists. Called from
    apps.orders.services.checkout for every line item, so a product's
    category — not just its vendor — can affect what commission the
    platform takes on that sale."""
    rule = CommissionRule.objects.filter(vendor=vendor, category=category).first()
    if rule is None:
        rule = CommissionRule.objects.filter(vendor__isnull=True, category=category).first()
    if rule is not None:
        return rule.rate
    return vendor.default_commission_rate
