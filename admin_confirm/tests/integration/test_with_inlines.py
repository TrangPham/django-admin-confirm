"""
Tests confirmation of add/change
on ModelAdmin that includes inlines

Does not test confirmation of inline changes
"""
from importlib import reload
from tests.factories import ShopFactory
from tests.market.models import GeneralManager, Shop, ShoppingMall, Town

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_CHANGE
from selenium.webdriver.support.ui import Select


class ConfirmWithInlinesTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.admin = shoppingmall_admin.ShoppingMallAdmin
        self.admin.inlines = [shoppingmall_admin.ShopInline]
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_should_have_hidden_form(self):
        mall = ShoppingMall.objects.create(name="mall")
        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/"
        )
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Change name
        name = self.selenium.find_element_by_name("name")
        name.send_keys("New Name")

        self.selenium.find_element_by_name("_continue").click()

        # Should have hidden form containing the updated name
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element_by_id("hidden-form")
        name = hidden_form.find_element_by_name("name")
        self.assertIn("New Name", name.get_attribute("value"))

        self.selenium.find_element_by_name("_continue").click()

        # Should persist change
        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)

    def test_should_have_hidden_formsets(self):
        # Not having formsets would cause a `ManagementForm tampered with` issue
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory(name=i) for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element_by_name("name")
        name.send_keys("New Name")

        self.selenium.find_element_by_name("_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element_by_id("hidden-form")
        hidden_form.find_element_by_name("ShoppingMall_shops-TOTAL_FORMS")
        self.selenium.find_element_by_name("_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)

    def test_should_have_saved_inline_changes(self):
        gm = GeneralManager.objects.create(name="gm")
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)

        shops = [ShopFactory(name=i) for i in range(3)]

        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element_by_name("name")
        name.send_keys("New Name")

        # Change shops via inline form
        select_shop = Select(
            self.selenium.find_element_by_name("ShoppingMall_shops-0-shop")
        )
        select_shop.select_by_value(str(shops[2].id))

        self.selenium.find_element_by_name("_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element_by_id("hidden-form")
        hidden_form.find_element_by_name("ShoppingMall_shops-TOTAL_FORMS")
        self.selenium.find_element_by_name("_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)
        self.assertIn(shops[2], mall.shops.all())
