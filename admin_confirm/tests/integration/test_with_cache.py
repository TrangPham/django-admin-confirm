"""
Tests confirmation of add/change
on ModelAdmin that utilize caches
"""
import os
import pkg_resources

from importlib import reload
from tests.factories import ShopFactory
from tests.market.models import GeneralManager, Item, ShoppingMall, Town

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_CHANGE
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.file_detector import LocalFileDetector
from django.core.files.uploadedfile import SimpleUploadedFile
from tempfile import NamedTemporaryFile


class ConfirmWithInlinesTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_models_without_files_should_not_have_confirmation_received(self):
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

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_name("_confirmation_received")

        self.selenium.find_element_by_name("_continue").click()

        # Should persist change
        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)

    def test_models_with_files_should_have_confirmation_received(self):
        item = Item.objects.create(name="item", price=1)
        self.selenium.get(
            self.live_server_url + f"/admin/market/item/{item.id}/change/"
        )
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Change price
        price = self.selenium.find_element_by_name("price")
        price.send_keys(2)

        self.selenium.find_element_by_name("_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element_by_id("hidden-form")
        price = hidden_form.find_element_by_name("price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element_by_name("_confirmation_received")
        self.selenium.find_element_by_name("_continue").click()

        item.refresh_from_db()

    def test_should_save_file_additions(self):
        item = Item.objects.create(name="item", price=1)

        self.selenium.get(
            self.live_server_url + f"/admin/market/item/{item.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element_by_name("price")
        price.send_keys(2)

        print(pkg_resources.get_distribution("selenium").version)
        # Upload a new file
        self.image_path = "screenshot.png"
        f = SimpleUploadedFile(
            name="test_file.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        f2 = NamedTemporaryFile()
        self.selenium.find_element_by_id("id_file").send_keys(
            # "/Users/thu/code/django_admin_confirm/screenshot.png"
            os.getcwd()
            + "/screenshot.png"
            # f2.name
            # os.path.abspath(self.image_path)
        )

        self.selenium.find_element_by_name("_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element_by_id("hidden-form")
        price = hidden_form.find_element_by_name("price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element_by_name("_confirmation_received")
        print(self.selenium.page_source)
        print("POST?")
        self.selenium.find_element_by_name("_continue").click()

        print(self.selenium.page_source)

        item.refresh_from_db()
        self.assertEqual(21, int(item.price))
        self.assertIn("screenshot.png", item.file.name)

    def test_should_save_file_changes(self):
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

    def test_should_remove_file_if_clear_selected(self):
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
