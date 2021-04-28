"""
Ensures that confirmations work with validators on the Model and on the Modelform.
"""

from logging import currentframe
from unittest import mock
from django.urls import reverse
from django.utils import timezone

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.models import Checkout, ItemSale
from tests.factories import (
    InventoryFactory,
    ItemFactory,
    ShopFactory,
    TransactionFactory,
)


import pytest
import pkg_resources
from importlib import reload
from tests.factories import ShopFactory
from tests.market.models import GeneralManager, ShoppingMall, Town

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_ADD, CONFIRM_CHANGE
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class ConfirmWithValidatorsTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.admin = shoppingmall_admin.ShoppingMallAdmin
        self.admin.inlines = [shoppingmall_admin.ShopInline]
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    @mock.patch("tests.market.models.ItemSale.clean")
    def test_can_confirm_for_models_with_validator_on_model_field(self, _mock_clean):
        # ItemSale.currency has a validator on it
        ItemFactory()
        TransactionFactory()

        self.selenium.get(self.live_server_url + f"/admin/market/itemsale/add/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        self.set_value(by=By.NAME, by_value="quantity", value="1")
        self.set_value(by=By.NAME, by_value="total", value="10.00")
        self.set_value(by=By.NAME, by_value="currency", value="USD")
        self.select_index(by=By.NAME, by_value="transaction", index=1)
        self.select_index(by=By.NAME, by_value="item", index=1)

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated name
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        currency = hidden_form.find_element(By.NAME, "currency")
        self.assertIn("USD", currency.get_attribute("value"))

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist change
        self.assertEqual(ItemSale.objects.count(), 1)

    def test_cannot_confirm_for_models_with_validator_on_model_field_if_validator_fails(
        self,
    ):
        # ItemSale.currency has a validator on it
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=10)
        TransactionFactory(shop=shop)

        self.selenium.get(self.live_server_url + f"/admin/market/itemsale/add/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        self.set_value(by=By.NAME, by_value="quantity", value="1")
        self.set_value(by=By.NAME, by_value="total", value="10.00")
        self.set_value(by=By.NAME, by_value="currency", value="FAKE")
        self.select_index(by=By.NAME, by_value="transaction", index=1)
        self.select_index(by=By.NAME, by_value="item", index=1)

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should show errors and not confirmation page
        self.assertNotIn("Confirm", self.selenium.page_source)
        self.assertIn("Invalid Currency", self.selenium.page_source)
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Now fix the issue
        self.set_value(by=By.NAME, by_value="currency", value="USD")
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated currency
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        currency = hidden_form.find_element(By.NAME, "currency")
        self.assertIn("USD", currency.get_attribute("value"))

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist change
        self.assertEqual(ItemSale.objects.count(), 1)

    def test_can_confirm_for_models_with_clean_overridden(self):
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=10)
        transaction = TransactionFactory(shop=shop)

        self.selenium.get(self.live_server_url + f"/admin/market/itemsale/add/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        self.set_value(by=By.NAME, by_value="quantity", value="9")
        self.set_value(by=By.NAME, by_value="total", value="10.00")
        self.set_value(by=By.NAME, by_value="currency", value="USD")
        self.select_index(by=By.NAME, by_value="transaction", index=1)
        self.select_index(by=By.NAME, by_value="item", index=1)

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Should have hidden form containing the updated currency
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        currency = hidden_form.find_element(By.NAME, "currency")
        self.assertIn("USD", currency.get_attribute("value"))

        # Confirm the change
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist change
        self.assertEqual(ItemSale.objects.count(), 1)

        # Ensure that the date and timestamp saved correctly
        item_sale = ItemSale.objects.first()
        self.assertEqual(item_sale.transaction, transaction)
        self.assertEqual(item_sale.item, item)
        self.assertEqual(item_sale.currency, "USD")

    def test_cannot_confirm_for_models_with_clean_overridden_if_clean_fails(self):
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=1)
        TransactionFactory(shop=shop)

        self.selenium.get(self.live_server_url + f"/admin/market/itemsale/add/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        self.set_value(by=By.NAME, by_value="quantity", value="9")
        self.set_value(by=By.NAME, by_value="total", value="10.00")
        self.set_value(by=By.NAME, by_value="currency", value="USD")
        self.select_index(by=By.NAME, by_value="transaction", index=1)
        self.select_index(by=By.NAME, by_value="item", index=1)

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should show errors and not confirmation page
        self.assertNotIn("Confirm", self.selenium.page_source)
        self.assertIn(
            "Shop does not have enough of the item stocked", self.selenium.page_source
        )
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Now fix the issue
        self.set_value(by=By.NAME, by_value="quantity", value="1")
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated currency
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        quantity = hidden_form.find_element(By.NAME, "quantity")
        self.assertIn("1", str(quantity.get_attribute("value")))

        # Confirm change
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist change
        self.assertEqual(ItemSale.objects.count(), 1)
