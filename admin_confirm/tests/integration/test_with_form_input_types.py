"""
Tests with different form input types
"""
from importlib import reload
from tests.market.models import Item

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import item_admin

from django.contrib.admin import VERTICAL
from admin_confirm.constants import CONFIRM_ADD
from selenium.webdriver.common.by import By


class ConfirmWithFormInputTypes(AdminConfirmIntegrationTestCase):
    def test_radio_input_should_work(self):
        self.admin = item_admin.ItemAdmin
        self.admin.confirm_add = True
        self.admin.confirm_change = True
        self.admin.confirmation_fields = ["currency", "price", "name"]
        self.admin.radio_fields = {"currency": VERTICAL}
        self.selenium.get(self.live_server_url + f"/admin/market/item/add/")

        # Should ask for confirmation of add
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys("24.00")

        # Select a radio option for currency
        currency = self.selenium.find_element(By.ID, "id_currency_0")
        currency.click()
        expected_value = currency.get_attribute("value")

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated name
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        name = hidden_form.find_element(By.NAME, "name")
        self.assertEqual("New Name", name.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist addition
        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.all().first()
        self.assertEqual("New Name", item.name)
        self.assertEqual(expected_value, item.currency)
        self.assertEqual(24, int(item.price))

        reload(item_admin)
