"""
Tests confirmation of add/change
on ModelAdmin that utilize caches
"""

import os
from django import forms

from tests.market.admin.item_admin import ItemAdmin
from tests.market.models import Item, ShoppingMall

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase

from admin_confirm.constants import CONFIRM_CHANGE, CONFIRM_ADD
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from django.core.files.uploadedfile import SimpleUploadedFile


class RequiredFileForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

    file = forms.FileField(required=True)


class ConfirmWithCacheTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_models_without_files_should_not_have_confirmation_received(self):
        mall = ShoppingMall.objects.create(name="mall")
        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
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
        self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Change price
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)
        self.selenium.find_element(By.ID, "id_currency_0").click()

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
        item = Item.objects.create(name="item", price=1, currency=Item.VALID_CURRENCIES[0][0])

        self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Upload a new file
        self.selenium.find_element(By.ID, "id_file").send_keys(os.getcwd() + "/screenshot.png")

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
        self.assertRegex(item.file.name, r"screenshot.*\.png$")

    def test_confirmation_page_should_not_render_required_hidden_file_input(self):
        self.setAdminAttributes(ItemAdmin, form=RequiredFileForm)
        item = Item.objects.create(name="item", price=1, currency=Item.VALID_CURRENCIES[0][0])

        self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Change a regular field and upload file so we reach confirmation flow.
        self.selenium.find_element(By.NAME, "price").send_keys(2)
        self.selenium.find_element(By.ID, "id_file").send_keys(os.getcwd() + "/screenshot.png")
        self.selenium.find_element(By.NAME, "_continue").click()
        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        hidden_file_input = hidden_form.find_element(By.NAME, "file")

        # Regression expectation: hidden form must not carry browser-required file control.
        self.assertIsNone(hidden_file_input.get_attribute("required"))

    def test_should_save_file_changes(self):
        with open("screenshot.png", "rb") as f:
            file = SimpleUploadedFile(
                name="old_file.jpg",
                content=f.read(),
                content_type="image/jpeg",
            )

        item = Item.objects.create(
            name="item", price=1, currency=Item.VALID_CURRENCIES[0][0], file=file
        )

        self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Upload a new file
        self.selenium.find_element(By.ID, "id_file").send_keys(os.getcwd() + "/screenshot.png")

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
        self.assertRegex(item.file.name, r"screenshot.*\.png$")

    def test_should_remove_file_if_clear_selected(self):
        with open("screenshot.png", "rb") as f:
            file = SimpleUploadedFile(
                name="old_file.jpg",
                content=f.read(),
                content_type="image/jpeg",
            )

        item = Item.objects.create(name="item", price=1, currency=Item.VALID_CURRENCIES[0][0], file=file)

        self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        price = self.selenium.find_element(By.NAME, "price")
        price.send_keys(2)

        # Choose to clear the existing file
        self.selenium.find_element(By.ID, "file-clear_id").click()
        self.assertTrue(
            self.selenium.find_element(By.XPATH, ".//*[@id='file-clear_id']").get_attribute(
                "checked"
            )
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

    def test_should_correctly_trigger_confirmation_only_when_file_changes(self):
        self.setAdminAttributes(ItemAdmin, confirmation_fields=["file"])
        item = None
        with self.subTest("New item with no file upload, should not trigger confirmation"):
            self.selenium.get(self.live_server_url + "/admin/market/item/add/")
            # Should be configured to ask for confirm on add
            self.assertIn(CONFIRM_ADD, self.selenium.page_source)

            self.selenium.find_element(By.NAME, "name").send_keys("New Item")
            self.selenium.find_element(By.NAME, "price").send_keys(1)
            self.selenium.find_element(By.ID, "id_currency_0").click()
            self.selenium.find_element(By.NAME, "_save").click()
            # Redirected to change page without confirmation since file was not uploaded
            self.assertTrue(self.selenium.current_url.endswith("/admin/market/item/"))

            item = Item.objects.get(name="New Item")
            self.assertEqual(item.price, 1)

        # Upload an image, should trigger confirmation (Detects change from no image to image)
        with self.subTest("Upload a file, should trigger confirmation"):
            self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
            self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

            self.selenium.find_element(By.ID, "id_file").send_keys(
                os.getcwd() + "/screenshot_confirm_add.png"
            )
            # Selecting "Save and continue editing" to stay on confirmation page after confirming change
            self.selenium.find_element(By.NAME, "_continue").click()
            # Should be on confirmation page since image was uploaded
            self.assertIn("Confirm", self.selenium.page_source)

            # Click "Yes, I'm sure" to confirm change
            self.selenium.find_element(By.NAME, "_confirmation_received")
            self.selenium.find_element(By.NAME, "_continue").click()
            # Because we selected "Save and continue editing", should be on change page after confirming
            self.assertTrue(
                self.selenium.current_url.endswith(f"/admin/market/item/{item.id}/change/")
            )

            item.refresh_from_db()
            self.assertIsNotNone(item.file)
            self.assertRegex(item.file.name, r"screenshot_confirm_add.*\.png$")

        # Make a change to another field without changing image, should not trigger confirmation
        with self.subTest(
            "Make a change to another field without changing image, should not trigger confirmation"
        ):
            self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
            self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

            price = self.selenium.find_element(By.NAME, "price")
            price.send_keys(2)
            self.selenium.find_element(By.NAME, "_save").click()
            # Should redirect to change page without confirmation since image was not changed
            self.assertTrue(self.selenium.current_url.endswith("/admin/market/item/"))

        # Upload a new file, should trigger confirmation (detects change from image to another image)
        with self.subTest("Upload a new image, should trigger confirmation"):
            self.selenium.get(self.live_server_url + f"/admin/market/item/{item.id}/change/")
            self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

            self.selenium.find_element(By.ID, "id_file").send_keys(os.getcwd() + "/screenshot.png")
            self.selenium.find_element(By.NAME, "_continue").click()
            # Should be on confirmation page since image was changed
            self.assertIn("Confirm", self.selenium.page_source)
            self.selenium.find_element(By.NAME, "_confirmation_received")
            self.selenium.find_element(By.NAME, "_continue").click()

            item.refresh_from_db()
            self.assertIsNotNone(item.file)
            self.assertRegex(item.file.name, r"screenshot.*\.png$")
