from decimal import Decimal

import pytest

from apps.commission.models import CommissionRule
from apps.orders.models import OrderItem
from apps.orders.tests.conftest import add_to_cart, do_checkout
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def test_checkout_uses_category_commission_rule(customer, address, vendor, category):
    CommissionRule.objects.create(vendor=None, category=category, rate=Decimal("2.00"))
    product = make_product(vendor, category, price="100.00")
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)

    order = do_checkout(customer, address)

    item = OrderItem.objects.get(order=order)
    assert item.commission_rate == Decimal("2.00")
    assert item.commission_amount == Decimal("2.00")


def test_checkout_falls_back_to_vendor_default_without_a_rule(customer, address, vendor, category):
    product = make_product(vendor, category, price="100.00")
    product.inventory.quantity = 10
    product.inventory.save(update_fields=["quantity"])
    add_to_cart(customer, product)

    order = do_checkout(customer, address)

    item = OrderItem.objects.get(order=order)
    assert item.commission_rate == vendor.default_commission_rate
