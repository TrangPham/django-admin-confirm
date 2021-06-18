"""
Tests confirmation of add/change
on ModelAdmin that utilize caches
and S3 as a storage backend
"""
import os

import pytest
import pkg_resources
import localstack_client.session

from importlib import reload
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from tests.market.models import Item

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_CHANGE


class ConfirmWithInlinesTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        session = localstack_client.session.Session(region_name="us-west-1")
        self.s3 = session.resource("s3")
        self.bucket = self.s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        # Delete all current files
        for obj in self.bucket.objects.all():
            obj.delete()
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        # Delete all current files
        for obj in self.bucket.objects.all():
            obj.delete()
        super().tearDown()

    def test_s3_is_being_used(self):
        self.assertEqual(settings.USE_S3, True)
        self.assertIsNotNone(settings.AWS_ACCESS_KEY_ID)
        self.assertEqual(
            settings.DEFAULT_FILE_STORAGE,
            "tests.storage_backends.PublicMediaStorage",
        )

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
        self.assertRegex(item.file.name, r"screenshot.*\.png$")
        self.assertEqual(21, int(item.price))

        # Check S3 for the file
        objects = [obj for obj in self.bucket.objects.all()]
        self.assertEqual(len(objects), 1)
        self.assertRegex(objects[0].key, r"screenshot.*\.png$")

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
        self.assertRegex(item.file.name, r"screenshot.*\.png$")

        # Check S3 for the file
        objects = [obj for obj in self.bucket.objects.all()]
        self.assertEqual(len(objects), 2)
        get_last_modified = lambda obj: int(obj.last_modified.strftime("%s"))
        objects_by_last_modified = [
            obj for obj in sorted(objects, key=get_last_modified)
        ]
        self.assertRegex(objects_by_last_modified[-1].key, r"screenshot.*\.png$")
        self.assertRegex(objects_by_last_modified[0].key, r"old_file.*\.jpg$")

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

        # Check S3 for the file
        # Since deleting from model instance in Django does not automatically
        #   delete from storage, the old file should still be in S3
        objects = [obj for obj in self.bucket.objects.all()]
        self.assertEqual(len(objects), 1)
        self.assertRegex(objects[0].key, r"old_file.*\.jpg$")
