from decimal import Decimal

import pytest

from apps.commission.models import CommissionRule
from apps.commission.selectors import resolve_commission_rate

pytestmark = pytest.mark.django_db


def test_falls_back_to_vendor_default_with_no_rules(vendor, category):
    assert resolve_commission_rate(vendor, category) == vendor.default_commission_rate


def test_category_wide_rule_applies_when_no_vendor_specific_rule(vendor, category):
    CommissionRule.objects.create(vendor=None, category=category, rate=Decimal("5.00"))

    assert resolve_commission_rate(vendor, category) == Decimal("5.00")


def test_vendor_specific_rule_takes_priority_over_category_wide(vendor, category):
    CommissionRule.objects.create(vendor=None, category=category, rate=Decimal("5.00"))
    CommissionRule.objects.create(vendor=vendor, category=category, rate=Decimal("2.50"))

    assert resolve_commission_rate(vendor, category) == Decimal("2.50")


def test_rule_for_different_category_does_not_apply(vendor, category):
    from apps.categories.models import Category

    other_category = Category.objects.create(name="Books", slug="books")
    CommissionRule.objects.create(vendor=None, category=other_category, rate=Decimal("1.00"))

    assert resolve_commission_rate(vendor, category) == vendor.default_commission_rate
