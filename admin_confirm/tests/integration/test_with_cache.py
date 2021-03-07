"""
Tests confirmation of add/change
on ModelAdmin that utilize caches
"""
import os
import pytest
import pkg_resources

from importlib import reload
from tests.market.models import Item, ShoppingMall

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_CHANGE
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from django.core.files.uploadedfile import SimpleUploadedFile


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
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated name
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        name = hidden_form.find_element(By.NAME, "name")
        self.assertIn("New Name", name.get_attribute("value"))

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element(By.NAME, "_confirmation_received")

        self.selenium.find_element(By.NAME, "_continue").click()

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
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        price = hidden_form.find_element(By.NAME, "price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_confirmation_received")
        self.selenium.find_element(By.NAME, "_continue").click()

        item.refresh_from_db()

    def test_should_save_file_additions(self):
        selenium_version = pkg_resources.get_distribution("selenium").parsed_version
        if selenium_version.major < 4:
            pytest.skip(
                "Known issue `https://github.com/SeleniumHQ/selenium/issues/8762` with this selenium version."
            )

        item = Item.objects.create(
            name="item", price=1, currency=Item.VALID_CURRENCIES[0][0]
        )

        self.selenium.get(
            self.live_server_url + f"/admin/market/item/{item.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Upload a new file
        self.selenium.find_element(By.ID, "id_file").send_keys(
            os.getcwd() + "/screenshot.png"
        )

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        price = hidden_form.find_element(By.NAME, "price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_confirmation_received")
        self.selenium.find_element(By.NAME, "_continue").click()

        item.refresh_from_db()
        self.assertEqual(21, int(item.price))
        self.assertIn("screenshot.png", item.file.name)

    def test_should_save_file_changes(self):
        selenium_version = pkg_resources.get_distribution("selenium").parsed_version
        if selenium_version.major < 4:
            pytest.skip(
                "Known issue `https://github.com/SeleniumHQ/selenium/issues/8762` with this selenium version."
            )

        file = SimpleUploadedFile(
            name="old_file.jpg",
            content=open("screenshot.png", "rb").read(),
            content_type="image/jpeg",
        )
        item = Item.objects.create(
            name="item", price=1, currency=Item.VALID_CURRENCIES[0][0], file=file
        )

        self.selenium.get(
            self.live_server_url + f"/admin/market/item/{item.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Upload a new file
        self.selenium.find_element(By.ID, "id_file").send_keys(
            os.getcwd() + "/screenshot.png"
        )

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        price = hidden_form.find_element(By.NAME, "price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_confirmation_received")
        self.selenium.find_element(By.NAME, "_continue").click()

        item.refresh_from_db()
        self.assertEqual(21, int(item.price))
        self.assertIn("screenshot.png", item.file.name)

    def test_should_remove_file_if_clear_selected(self):
        file = SimpleUploadedFile(
            name="old_file.jpg",
            content=open("screenshot.png", "rb").read(),
            content_type="image/jpeg",
        )
        item = Item.objects.create(
            name="item", price=1, currency=Item.VALID_CURRENCIES[0][0], file=file
        )

        self.selenium.get(
            self.live_server_url + f"/admin/market/item/{item.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Choose to clear the existing file
        self.selenium.find_element(By.ID, "file-clear_id").click()
        self.assertTrue(
            self.selenium.find_element(
                By.XPATH, ".//*[@id='file-clear_id']"
            ).get_attribute("checked")
        )

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated price
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        price = hidden_form.find_element(By.NAME, "price")
        self.assertEqual("21.00", price.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_confirmation_received")
        self.selenium.find_element(By.NAME, "_continue").click()

        item.refresh_from_db()
        self.assertEqual(21, int(item.price))
        # Should have cleared `file` since clear was selected
        self.assertFalse(item.file)
