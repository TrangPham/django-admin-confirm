"""
Tests with different form input types
"""
from datetime import timedelta
from django.utils import timezone
from importlib import reload
from tests.factories import ShopFactory, TransactionFactory
from tests.market.models import GeneralManager, Item, ShoppingMall, Town

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import item_admin, shoppingmall_admin

from django.contrib.admin import VERTICAL
from admin_confirm.constants import CONFIRM_ADD, CONFIRM_CHANGE
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class ConfirmWithFormInputTypes(AdminConfirmIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        i_admin = item_admin.ItemAdmin
        i_admin.confirm_add = True
        i_admin.confirm_change = True
        i_admin.confirmation_fields = ["currency", "price", "name"]
        i_admin.radio_fields = {"currency": VERTICAL}

        mall_admin = shoppingmall_admin.ShoppingMallAdmin
        mall_admin.raw_id_fields = ["general_manager"]
        mall_admin.inlines = []
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        reload(shoppingmall_admin)
        reload(item_admin)
        return super().tearDownClass()

    def test_radio_input_should_work(self):
        self.selenium.get(self.live_server_url + f"/admin/market/item/add/")
        self.assertIn("radio", self.selenium.page_source)

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

    def test_raw_id_fields_should_work(self):
        gm1 = GeneralManager.objects.create(name="gm1")
        shops = [ShopFactory(name=i) for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm1, town=town)
        mall.shops.set(shops)

        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        # Set general_manager via raw_id_fields
        gm2 = GeneralManager.objects.create(name="gm2")
        general_manager = self.selenium.find_element(By.NAME, "general_manager")
        general_manager.clear()
        general_manager.send_keys(str(gm2.id))

        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)
        self.selenium.find_element(By.NAME, "_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)
        self.assertEqual(gm2, mall.general_manager)

    def test_datetime_and_field_should_work(self):
        original_timestamp = timezone.now() - timedelta(hours=1)
        transaction = TransactionFactory(timestamp=original_timestamp)

        self.selenium.get(
            self.live_server_url + f"/admin/market/transaction/{transaction.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Set date via text input
        date_input = self.selenium.find_element(By.ID, "id_date")
        date_input.clear()
        date_input.send_keys("2021-01-01")
        self.assertEqual(date_input.get_attribute("value"), "2021-01-01")

        # Set timestamp via text input
        timestamp_date = self.selenium.find_element(By.ID, "id_timestamp_0")
        timestamp_date.clear()
        timestamp_date.send_keys(str(timezone.now().date()))
        timestamp_time = self.selenium.find_element(By.ID, "id_timestamp_1")
        timestamp_time.clear()
        timestamp_time.send_keys(str(timezone.now().time()))

        # Click save and continue
        self.selenium.find_element(By.NAME, "_continue").click()

        # Click Yes I'm Sure on confirmation page
        self.assertIn("Confirm", self.selenium.page_source)
        self.selenium.find_element(By.NAME, "_continue").click()

        transaction.refresh_from_db()
        self.assertEqual(str(transaction.date), "2021-01-01")
        self.assertTrue(transaction.timestamp > original_timestamp)
