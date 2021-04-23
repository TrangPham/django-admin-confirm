from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.admin import ItemAdmin, ShoppingMallAdmin
from tests.market.models import GeneralManager, Item, ShoppingMall, Town
from tests.factories import ItemFactory, ShopFactory

from admin_confirm.constants import CACHE_KEYS, CONFIRMATION_RECEIVED


@mock.patch.object(ShoppingMallAdmin, "inlines", [])
class TestConfirmSaveActions(AdminConfirmTestCase):
    def test_simple_add_with_save(self):
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
            rendered_content=response.rendered_content,
            save_action="_save",
            multipart_form=True,
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
        data[CONFIRMATION_RECEIVED] = True
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

    def test_simple_change_with_continue(self):
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
            rendered_content=response.rendered_content,
            save_action="_continue",
            multipart_form=True,
        )

        # # Should have cached the unsaved item
        # cached_item = cache.get(CACHE_KEYS["object"])
        # self.assertIsNotNone(cached_item)
        # self.assertIsNone(cached_item.id)
        # self.assertEqual(cached_item.name, data["name"])
        # self.assertEqual(cached_item.price, data["price"])
        # self.assertEqual(cached_item.currency, data["currency"])

        # Should not have saved the changes yet
        self.assertEqual(Item.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data[CONFIRMATION_RECEIVED] = True
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

    def test_file_and_image_add_addanother(self):
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
            "_addanother": True,
        }
        response = self.client.post(reverse("admin:market_item_add"), data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content,
            save_action="_addanother",
            multipart_form=True,
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

        # Should not have saved the item yet
        self.assertEqual(Item.objects.count(), 0)

        # Click "Yes, I'm Sure"
        confirmation_data = data.copy()
        del confirmation_data["_confirm_add"]
        del confirmation_data["image"]
        del confirmation_data["file"]
        confirmation_data[CONFIRMATION_RECEIVED] = True
        response = self.client.post(
            reverse("admin:market_item_add"), data=confirmation_data
        )

        # Should have redirected to changelist
        self.assertEqual(response.status_code, 302)
        # Should show add page since "add another" was selected
        self.assertEqual(response.url, "/admin/market/item/add/")

        # Should have saved item
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.all().first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.price, data["price"])
        self.assertEqual(saved_item.currency, data["currency"])
        self.assertIsNotNone(saved_item.file)
        self.assertIsNotNone(saved_item.image)

        self.assertRegex(saved_item.file.name, r"test_file_.*\.jpg$")
        self.assertRegex(saved_item.image.name, r"test_image_.*\.jpg$")

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    def test_file_and_image_change_with_saveasnew(self):
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
        ItemAdmin.save_as = True
        ItemAdmin.save_as_continue = True
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
            "_saveasnew": True,
        }
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content,
            save_action="_saveasnew",
            multipart_form=True,
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

        # Should not have saved the changes yet
        self.assertEqual(Item.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.name, "Not name")
        self.assertIsNotNone(item.file)
        self.assertIsNotNone(item.image)

        # Click "Yes, I'm Sure"
        del data["_confirm_change"]
        data["image"] = ""
        data[CONFIRMATION_RECEIVED] = True
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data=data)

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/item/{item.id + 1}/change/")

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
        self.assertIsNotNone(new_item.image)
        self.assertRegex(new_item.image.name, r"test_image2_.*\.jpg$")

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

        # Should not have cached the unsaved object
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNone(cached_item)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_add"]
        confirmation_received_data[CONFIRMATION_RECEIVED] = True

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

    def test_relation_change_with_saveasnew(self):
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
            "_saveasnew": True,
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
            rendered_content=response.rendered_content, save_action="_saveasnew"
        )

        # Should not have cached the unsaved obj
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNone(cached_item)

        # Should not have saved changes yet
        self.assertEqual(ShoppingMall.objects.count(), 1)
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data.copy()
        del confirmation_received_data["_confirm_change"]

        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/",
            data=confirmation_received_data,
        )

        # Should not have redirected to changelist
        self.assertEqual(
            response.url, f"/admin/market/shoppingmall/{mall.id + 1}/change/"
        )

        # Should have saved obj
        self.assertEqual(ShoppingMall.objects.count(), 2)
        # Should not have changed old obj
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Should have created new obj
        saved_item = ShoppingMall.objects.filter(id=mall.id + 1).first()
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.general_manager, gm2)
        self.assertEqual(saved_item.town, town2)

        for shop in saved_item.shops.all():
            self.assertIn(shop, shops2)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))
