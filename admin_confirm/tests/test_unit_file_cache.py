"""
Ensure that files are saved during confirmation
Without file changes, Django is relied on

With file changes, we cache the object, save it with
the files if new, or add files to existing obj and save

Then send the rest of the changes to Django to handle

This is arguably the most we fiddle with the Django request
Thus we should test it extensively
"""
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from admin_confirm.tests.helpers import AdminConfirmTestCase
from admin_confirm.constants import CACHE_KEYS

from tests.market.admin import ItemAdmin
from tests.market.models import Item
from tests.factories import ItemFactory


class FileCacheUnitTests(AdminConfirmTestCase):
    def setUp(self):
        self.image_path = "screenshot.png"
        f = SimpleUploadedFile(
            name="test_file.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        i = SimpleUploadedFile(
            name="test_image.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        self.item = ItemFactory(name="Not name", file=f, image=i)

        return super().setUp()

    def test_save_as_continue_true_should_not_redirect_to_changelist(self):
        item = self.item
        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        ItemAdmin.fields = ["name", "price", "file", "image", "currency"]
        ItemAdmin.save_as = True
        ItemAdmin.save_as_continue = True

        # Upload new image and remove file
        i2 = SimpleUploadedFile(
            name="test_image2.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        # Request.POST
        data = {
            "id": item.id,
            "name": "name",
            "price": 2.0,
            "file": "",
            "file-clear": "on",
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_change": True,
            "_saveasnew": True,
        }

        # Set cache
        cache_item = Item(
            name=data["name"],
            price=data["price"],
            currency=data["currency"],
            image=i2,
        )

        cache.set(CACHE_KEYS["object"], cache_item)
        cache.set(CACHE_KEYS["post"], data)

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["_confirmation_received"] = True

        with mock.patch.object(ItemAdmin, "message_user") as message_user:
            response = self.client.post(
                f"/admin/market/item/{self.item.id}/change/", data=data
            )
            # Should show message to user with correct obj and path
            message_user.assert_called_once()
            message = message_user.call_args[0][1]
            self.assertIn("/admin/market/item/2/change/", message)
            self.assertIn(data["name"], message)
            self.assertIn("You may edit it again below.", message)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/{self.item.id + 1}/change/")

        # Should not have changed existing item
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")
        self.assertEqual(item.file.name.count("test_file"), 1)
        self.assertEqual(item.image.name.count("test_image2"), 0)
        self.assertEqual(item.image.name.count("test_image"), 1)

        # Should have saved new item
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.filter(id=item.id + 1).first()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.name, data["name"])
        self.assertEqual(new_item.price, data["price"])
        self.assertEqual(new_item.currency, data["currency"])
        self.assertFalse(new_item.file)
        self.assertEqual(new_item.image.name.count("test_image2"), 1)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_save_as_continue_false_should_redirect_to_changelist(self):
        item = self.item
        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        ItemAdmin.fields = ["name", "price", "file", "image", "currency"]
        ItemAdmin.save_as = True
        ItemAdmin.save_as_continue = False

        # Upload new image and remove file
        i2 = SimpleUploadedFile(
            name="test_image2.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        # Request.POST
        data = {
            "id": item.id,
            "name": "name",
            "price": 2.0,
            "file": "",
            "file-clear": "on",
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_change": True,
            "_saveasnew": True,
        }

        # Set cache
        cache_item = Item(
            name=data["name"],
            price=data["price"],
            currency=data["currency"],
            image=i2,
        )

        cache.set(CACHE_KEYS["object"], cache_item)
        cache.set(CACHE_KEYS["post"], data)

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["_confirmation_received"] = True

        with mock.patch.object(ItemAdmin, "message_user") as message_user:
            response = self.client.post(
                f"/admin/market/item/{self.item.id}/change/", data=data
            )
            # Should show message to user with correct obj and path
            message_user.assert_called_once()
            message = message_user.call_args[0][1]
            self.assertIn("/admin/market/item/2/change/", message)
            self.assertIn(data["name"], message)
            self.assertNotIn("You may edit it again below.", message)

        # Should have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/")

        # Should not have changed existing item
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")
        self.assertEqual(item.file.name.count("test_file"), 1)
        self.assertEqual(item.image.name.count("test_image2"), 0)
        self.assertEqual(item.image.name.count("test_image"), 1)

        # Should have saved new item
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.filter(id=item.id + 1).first()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.name, data["name"])
        self.assertEqual(new_item.price, data["price"])
        self.assertEqual(new_item.currency, data["currency"])
        self.assertFalse(new_item.file)
        self.assertEqual(new_item.image.name.count("test_image2"), 1)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_without_any_file_changes(self):
        item = self.item
        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        ItemAdmin.fields = ["name", "price", "file", "image", "currency"]
        ItemAdmin.save_as = True
        ItemAdmin.save_as_continue = True

        # Request.POST
        data = {
            "id": item.id,
            "name": "name",
            "price": 2.0,
            "file": "",
            "image": "",
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_change": True,
            "_saveasnew": True,
        }

        # Set cache
        cache_item = Item(
            name=data["name"],
            price=data["price"],
            currency=data["currency"],
        )

        cache.set(CACHE_KEYS["object"], cache_item)
        cache.set(CACHE_KEYS["post"], data)

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["_confirmation_received"] = True

        with mock.patch.object(ItemAdmin, "message_user") as message_user:
            response = self.client.post(
                f"/admin/market/item/{self.item.id}/change/", data=data
            )
            # Should show message to user with correct obj and path
            message_user.assert_called_once()
            message = message_user.call_args[0][1]
            self.assertIn("/admin/market/item/2/change/", message)
            self.assertIn(data["name"], message)
            self.assertIn("You may edit it again below.", message)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/{self.item.id + 1}/change/")

        # Should not have changed existing item
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")
        self.assertEqual(item.file.name.count("test_file"), 1)
        self.assertEqual(item.image.name.count("test_image2"), 0)
        self.assertEqual(item.image.name.count("test_image"), 1)

        # Should have saved new item
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.filter(id=item.id + 1).first()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.name, data["name"])
        self.assertEqual(new_item.price, data["price"])
        self.assertEqual(new_item.currency, data["currency"])
        # In Django (by default), the save as new does not transfer over the files
        self.assertFalse(new_item.file)
        self.assertFalse(new_item.image)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_add_with_upload_file(self):
        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        ItemAdmin.fields = ["name", "price", "file", "image", "currency"]
        ItemAdmin.save_as = True
        ItemAdmin.save_as_continue = True

        # Request.POST
        data = {
            "name": "name",
            "price": 2.0,
            "image": "",
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_add": True,
            "_save": True,
        }

        # Upload new file
        f2 = SimpleUploadedFile(
            name="test_file2.jpg",
            content=open(self.image_path, "rb").read(),
            content_type="image/jpeg",
        )
        # Set cache
        cache_item = Item(
            name=data["name"], price=data["price"], currency=data["currency"], file=f2
        )

        cache.set(CACHE_KEYS["object"], cache_item)
        cache.set(CACHE_KEYS["post"], data)

        # Click "Yes, I'm Sure"
        del data["_confirm_add"]
        data["_confirmation_received"] = True

        with mock.patch.object(ItemAdmin, "message_user") as message_user:
            response = self.client.post(f"/admin/market/item/add/", data=data)
            # Should show message to user with correct obj and path
            message_user.assert_called_once()
            message = message_user.call_args[0][1]
            self.assertIn("/admin/market/item/2/change/", message)
            self.assertIn(data["name"], message)
            self.assertNotIn("You may edit it again below.", message)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/")

        # Should not have changed existing item
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Not name")
        self.assertEqual(self.item.file.name.count("test_file"), 1)
        self.assertEqual(self.item.image.name.count("test_image2"), 0)
        self.assertEqual(self.item.image.name.count("test_image"), 1)

        # Should have saved new item
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.filter(id=self.item.id + 1).first()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.name, data["name"])
        self.assertEqual(new_item.price, data["price"])
        self.assertEqual(new_item.currency, data["currency"])
        # In Django (by default), the save as new does not transfer over the files
        self.assertIn("test_file2", new_item.file.name)
        self.assertFalse(new_item.image)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))