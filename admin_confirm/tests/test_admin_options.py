from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.admin import ItemAdmin, ShoppingMallAdmin
from tests.market.models import GeneralManager, Item, ShoppingMall, Town
from tests.factories import ItemFactory, ShopFactory

from admin_confirm.constants import CACHE_KEYS


class TestAdminOptions(AdminConfirmTestCase):
    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "fields", ["name", "town"])
    def test_m2m_field_not_in_fields(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )

        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
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
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        # should have presevered the fields that are not in form
        self.assertEqual(saved_item.general_manager, gm)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "exclude", ["shops"])
    def test_m2m_field_in_exclude(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )
        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
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
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        self.assertEqual(saved_item.general_manager, gm2)
        # should have presevered the fields that are not in form (exclude)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "exclude", ["shops", "name"])
    def test_confirmation_fields_in_exclude(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )
        # Should not be shown confirmation page
        # SInce we used "Save and Continue", should show change page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved the non excluded fields
        mall.refresh_from_db()
        for shop in shops:
            self.assertIn(shop, mall.shops.all())
        self.assertEqual(mall.name, "mall")
        # Should have saved other fields
        self.assertEqual(mall.town, town2)
        self.assertEqual(mall.general_manager, gm2)

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "readonly_fields", ["shops", "name"])
    def test_confirmation_fields_in_readonly(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )
        # Should not be shown confirmation page
        # SInce we used "Save and Continue", should show change page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved the non excluded fields
        mall.refresh_from_db()
        for shop in shops:
            self.assertIn(shop, mall.shops.all())
        self.assertEqual(mall.name, "mall")
        # Should have saved other fields
        self.assertEqual(mall.town, town2)
        self.assertEqual(mall.general_manager, gm2)

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "readonly_fields", ["shops"])
    def test_readonly_fields_should_not_change(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        shops2 = [ShopFactory() for i in range(3)]
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data=data
        )
        # Should be shown confirmation page
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
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
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        self.assertEqual(saved_item.general_manager, gm2)
        # should have presevered the fields that are not in form (exclude)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))
