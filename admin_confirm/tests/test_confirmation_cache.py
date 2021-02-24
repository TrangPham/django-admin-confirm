from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.admin import ItemAdmin, ShoppingMallAdmin
from tests.market.models import GeneralManager, Item, ShoppingMall, Town
from tests.factories import ItemFactory, ShopFactory

from admin_confirm.constants import CACHE_KEYS


class TestConfirmationCache(AdminConfirmTestCase):
    def test_simple_add(self):
        # Load the Add Item Page
        ItemAdmin.confirm_add = True
        response = self.client.get(reverse("admin:market_item_add"))

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_add"))
        self.assertIn("_confirm_add", response.rendered_content)

        # Click "Save"
        data = {
            "name": "name",
            "price": 2.0,
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_item_add"), data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_save"
        )

        # Should have cached the unsaved item
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)
        self.assertEqual(cached_item.name, data["name"])
        self.assertEqual(cached_item.price, data["price"])
        self.assertEqual(cached_item.currency, data["currency"])

        # Should not have saved the item yet
        self.assertEqual(Item.objects.count(), 0)

        # Click "Yes, I'm Sure"
        del data["_confirm_add"]
        data["_confirmation_received"] = True
        response = self.client.post(reverse("admin:market_item_add"), data=data)

        # Should have redirected to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/item/")

        # Should have saved item
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.price, data["price"])
        self.assertEqual(saved_item.currency, data["currency"])

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_simple_change(self):
        item = ItemFactory(name="Not name")

        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        response = self.client.get(f"/admin/market/item/{item.id}/change/")

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_change"))
        self.assertIn("_confirm_change", response.rendered_content)

        # Click "Save And Continue"
        data = {
            "id": item.id,
            "name": "name",
            "price": 2.0,
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Should have cached the unsaved item
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)
        self.assertEqual(cached_item.name, data["name"])
        self.assertEqual(cached_item.price, data["price"])
        self.assertEqual(cached_item.currency, data["currency"])

        # cached_change_message = cache.get(CACHE_KEYS["change_message"])
        # self.assertIsNotNone(cached_change_message)
        # self.assertIn("changed", cached_change_message[0].keys())

        # Should not have saved the changes yet
        self.assertEqual(Item.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["_confirmation_received"] = True
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/{item.id}/change/")

        # Should have saved item
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.price, data["price"])
        self.assertEqual(saved_item.currency, data["currency"])

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_file_and_image_add(self):
        # Load the Add Item Page
        ItemAdmin.confirm_add = True
        response = self.client.get(reverse("admin:market_item_add"))

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_add"))
        self.assertIn("_confirm_add", response.rendered_content)

        # Select files
        image_path = "screenshot.png"
        f = SimpleUploadedFile(
            name="test_file.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        i = SimpleUploadedFile(
            name="test_image.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        # Click "Save"
        data = {
            "name": "name",
            "price": 2.0,
            "currency": Item.VALID_CURRENCIES[0][0],
            "file": f,
            "image": i,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_item_add"), data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_save"
        )

        # Should have cached the unsaved item
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)
        self.assertEqual(cached_item.name, data["name"])
        self.assertEqual(cached_item.price, data["price"])
        self.assertEqual(cached_item.currency, data["currency"])
        self.assertEqual(cached_item.file, data["file"])
        self.assertEqual(cached_item.image, data["image"])

        # cached_change_message = cache.get(CACHE_KEYS["change_message"])
        # self.assertIsNotNone(cached_change_message)
        # self.assertIn("added", cached_change_message[0].keys())

        # Should not have saved the item yet
        self.assertEqual(Item.objects.count(), 0)

        # Click "Yes, I'm Sure"
        confirmation_data = data.copy()
        del confirmation_data["_confirm_add"]
        del confirmation_data["image"]
        del confirmation_data["file"]
        confirmation_data["_confirmation_received"] = True
        response = self.client.post(
            reverse("admin:market_item_add"), data=confirmation_data
        )

        # Should have redirected to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/item/")

        # Should have saved item
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.price, data["price"])
        self.assertEqual(saved_item.currency, data["currency"])
        self.assertEqual(saved_item.file, data["file"])
        self.assertEqual(saved_item.image, data["image"])

        self.assertEqual(saved_item.file.name, "test_file.jpg")
        self.assertEqual(saved_item.image.name, "test_image.jpg")

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_file_and_image_change(self):
        item = ItemFactory(name="Not name")
        # Select files
        image_path = "screenshot.png"
        f = SimpleUploadedFile(
            name="test_file.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        i = SimpleUploadedFile(
            name="test_image.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        item.file = f
        item.image = i
        item.save()

        # Load the Change Item Page
        ItemAdmin.confirm_change = True
        ItemAdmin.fields = ["name", "price", "file", "image", "currency"]
        response = self.client.get(f"/admin/market/item/{item.id}/change/")

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_change"))
        self.assertIn("_confirm_change", response.rendered_content)

        # Upload new image and remove file
        i2 = SimpleUploadedFile(
            name="test_image2.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        # Click "Save And Continue"
        data = {
            "id": item.id,
            "name": "name",
            "price": 2.0,
            "image": i2,
            "file": "",
            "file-clear": "on",
            "currency": Item.VALID_CURRENCIES[0][0],
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Should have cached the unsaved item
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)
        self.assertEqual(cached_item.name, data["name"])
        self.assertEqual(cached_item.price, data["price"])
        self.assertEqual(cached_item.currency, data["currency"])
        self.assertFalse(cached_item.file.name)
        self.assertEqual(cached_item.image, i2)

        # cached_change_message = cache.get(CACHE_KEYS["change_message"])
        # self.assertIsNotNone(cached_change_message)
        # self.assertIn("changed", cached_change_message[0].keys())

        # Should not have saved the changes yet
        self.assertEqual(Item.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")
        self.assertIsNotNone(item.file)
        self.assertIsNotNone(item.image)

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["image"] = ""
        data["_confirmation_received"] = True
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/{item.id}/change/")

        # Should have saved item
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.price, data["price"])
        self.assertEqual(saved_item.currency, data["currency"])
        self.assertFalse(saved_item.file)
        self.assertEqual(saved_item.image, i2)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_relations_add(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")

        # Load the Add ShoppingMall Page
        ShoppingMallAdmin.confirm_add = True
        response = self.client.get(reverse("admin:market_shoppingmall_add"))

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_add"))
        self.assertIn("_confirm_add", response.rendered_content)

        # Click "Save"
        data = {
            "name": "name",
            "shops": [s.id for s in shops],
            "general_manager": gm.id,
            "town": town.id,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data=data)

        # Should be shown confirmation page
        self._assertManyToManyFormHtml(
            rendered_content=response.rendered_content,
            options=shops,
            selected_ids=data["shops"],
        )
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_save"
        )

        # Should have cached the unsaved object
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)

        # cached_change_message = cache.get(CACHE_KEYS["change_message"])
        # self.assertIsNotNone(cached_change_message)
        # self.assertIn("added", cached_change_message[0].keys())

        # Should not have saved the object yet
        self.assertEqual(ShoppingMall.objects.count(), 0)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_add"]
        confirmation_received_data["_confirmation_received"] = True

        response = self.client.post(
            reverse("admin:market_shoppingmall_add"), data=confirmation_received_data
        )

        # Should have redirected to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shoppingmall/")

        # Should have saved object
        self.assertEqual(ShoppingMall.objects.count(), 1)
        saved_item = ShoppingMall.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.general_manager, gm)
        self.assertEqual(saved_item.town, town)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_relation_change(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        # Load the Change ShoppingMall Page
        ShoppingMallAdmin.confirm_change = True
        response = self.client.get(f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should be asked for confirmation
        self.assertTrue(response.context_data.get("confirm_change"))
        self.assertIn("_confirm_change", response.rendered_content)

        # Click "Save"
        data = {
            "id": mall.id,
            "name": "name",
            "shops": [s.id for s in shops2],
            "general_manager": gm2.id,
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )

        # Should be shown confirmation page
        self._assertManyToManyFormHtml(
            rendered_content=response.rendered_content,
            options=shops,
            selected_ids=data["shops"],
        )
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Should have cached the unsaved obj
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNotNone(cached_item)
        self.assertIsNone(cached_item.id)

        # cached_change_message = cache.get(CACHE_KEYS["change_message"])
        # self.assertIsNotNone(cached_change_message)
        # self.assertIn("changed", cached_change_message[0].keys())

        # Should not have saved changes yet
        self.assertEqual(ShoppingMall.objects.count(), 1)
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_change"]
        confirmation_received_data["_confirmation_received"] = True

        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/",
            data=confirmation_received_data,
        )

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved obj
        self.assertEqual(ShoppingMall.objects.count(), 1)
        saved_item = ShoppingMall.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.general_manager, gm2)
        self.assertEqual(saved_item.town, town2)

        for shop in saved_item.shops.all():
            self.assertIn(shop, shops2)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))
