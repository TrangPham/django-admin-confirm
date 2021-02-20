from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.options import TO_FIELD_VAR
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse


from tests.market.admin import ItemAdmin, InventoryAdmin
from tests.market.models import Item, Inventory, ShoppingMall
from tests.factories import ItemFactory, ShopFactory, InventoryFactory


class TestConfirmChangeAndAddM2MField(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="super", email="super@email.org", password="pass"
        )

    def setUp(self):
        self.client.force_login(self.superuser)
        self.factory = RequestFactory()

    def test_post_add_without_confirm_add_m2m(self):
        data = {"name": "name", "price": 2.0, "currency": Item.VALID_CURRENCIES[0]}
        response = self.client.post(reverse("admin:market_item_add"), data)
        # Redirects to item changelist and item is added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/item/")
        self.assertEqual(Item.objects.count(), 1)

    def test_post_add_with_confirm_add_m2m(self):
        item = ItemFactory()
        shop = ShopFactory()
        data = {"shop": shop.id, "item": item.id, "quantity": 5, "_confirm_add": True}
        response = self.client.post(reverse("admin:market_inventory_add"), data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/inventory/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = {"shop": str(shop.id), "item": str(item.id), "quantity": str(5)}
        # self.assertEqual(response.context_data["form_data"], form_data)
        for k, v in form_data.items():
            self.assertIn(
                f'<input type="hidden" name="{ k }" value="{ v }">',
                response.rendered_content,
            )

        # Should not have been added yet
        self.assertEqual(Inventory.objects.count(), 0)

    def test_m2m_field_post_change_with_confirm_change(self):
        shops = [ShopFactory() for i in range(10)]
        shopping_mall = ShoppingMall.objects.create(name="My Mall")
        shopping_mall.shops.set(shops)
        # Currently ShoppingMall configured with confirmation_fields = ['name']
        data = {
            "name": "Not My Mall",
            "shops": "1",
            "id": shopping_mall.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{shopping_mall.id}/change/", data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/shoppingmall/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = {
            "name": "Not My Mall",
            "shops": "1",
            "id": str(shopping_mall.id),
        }

        for k, v in form_data.items():
            self.assertIn(
                f'<input type="hidden" name="{ k }" value="{ v }">',
                response.rendered_content,
            )

        # Hasn't changed item yet
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.name, "My Mall")

    def test_m2m_field_post_change_with_confirm_change_multiple_selected(self):
        shops = [ShopFactory() for i in range(10)]
        shopping_mall = ShoppingMall.objects.create(name="My Mall")
        shopping_mall.shops.set(shops)
        # Currently ShoppingMall configured with confirmation_fields = ['name']
        data = {
            "name": "Not My Mall",
            "shops": ["1", "2", "3"],
            "id": shopping_mall.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{shopping_mall.id}/change/", data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/shoppingmall/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = [
            ("name", "Not My Mall"),
            ("shops", "1"),
            ("shops", "2"),
            ("shops", "3"),
            ("id", str(shopping_mall.id)),
        ]

        for k, v in form_data:
            self.assertIn(
                f'<input type="hidden" name="{ k }" value="{ v }">',
                response.rendered_content,
            )

        # Hasn't changed item yet
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.name, "My Mall")

    def test_post_change_without_confirm_change_m2m_value(self):
        # TODO
        shop = ShopFactory(name="bob")
        data = {"name": "sally"}
        response = self.client.post(f"/admin/market/shop/{shop.id}/change/", data)
        # Redirects to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shop/")
        # Shop has changed
        shop.refresh_from_db()
        self.assertEqual(shop.name, "sally")

    def test_form_invalid_m2m_value(self):
        # TODO
        self.assertEqual(InventoryAdmin.confirmation_fields, ["quantity"])

        inventory = InventoryFactory(quantity=1)
        data = {
            "quantity": 1,
            "shop": "Invalid value",
            "item": "Invalid value",
            "id": inventory.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
        }
        response = self.client.post(
            f"/admin/market/inventory/{inventory.id}/change/", data
        )

        # Form invalid should show errors on form
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data.get("errors"))
        self.assertEqual(
            response.context_data["errors"][0],
            ["Select a valid choice. That choice is not one of the available choices."],
        )
        # Should not have updated inventory
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 1)

    def test_confirmation_fields_set_with_confirm_change_on_m2m_field(self):
        # TODO
        self.assertEqual(InventoryAdmin.confirmation_fields, ["quantity"])

        inventory = InventoryFactory()
        another_shop = ShopFactory()
        data = {
            "quantity": inventory.quantity,
            "id": inventory.id,
            "item": inventory.item.id,
            "shop": another_shop.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
        }
        response = self.client.post(
            f"/admin/market/inventory/{inventory.id}/change/", data
        )

        # Should not have shown confirmation page since shop did not change
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("admin:market_inventory_changelist"))
        # Should have updated inventory
        inventory.refresh_from_db()
        self.assertEqual(inventory.shop, another_shop)

    def test_confirmation_fields_set_with_confirm_add_on_a_m2m_field(self):
        # TODO
        self.assertEqual(InventoryAdmin.confirmation_fields, ["quantity"])

        item = ItemFactory()
        shop = ShopFactory()

        # Don't set quantity - let it default
        data = {"shop": shop.id, "item": item.id, "_confirm_add": True}
        response = self.client.post(reverse("admin:market_inventory_add"), data)
        # No confirmation needed
        self.assertEqual(response.status_code, 302)

        # Should have been added
        self.assertEqual(Inventory.objects.count(), 1)
        new_inventory = Inventory.objects.all().first()
        self.assertEqual(new_inventory.shop, shop)
        self.assertEqual(new_inventory.item, item)
        self.assertEqual(
            new_inventory.quantity, Inventory._meta.get_field("quantity").default
        )
