from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.options import TO_FIELD_VAR
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.admin import ItemAdmin, InventoryAdmin
from tests.market.models import Item, Inventory, ShoppingMall
from tests.factories import ItemFactory, ShopFactory, InventoryFactory


class TestConfirmChangeAndAdd(AdminConfirmTestCase):
    def test_get_add_without_confirm_add(self):
        ItemAdmin.confirm_add = False
        response = self.client.get(reverse("admin:market_item_add"))
        self.assertFalse(response.context_data.get("confirm_add"))
        self.assertNotIn("_confirm_add", response.rendered_content)

    def test_get_add_with_confirm_add(self):
        response = self.client.get(reverse("admin:market_inventory_add"))
        self.assertTrue(response.context_data.get("confirm_add"))
        self.assertIn("_confirm_add", response.rendered_content)

    def test_get_change_without_confirm_change(self):
        response = self.client.get(reverse("admin:market_shop_add"))
        self.assertFalse(response.context_data.get("confirm_change"))
        self.assertNotIn("_confirm_change", response.rendered_content)

    def test_get_change_with_confirm_change(self):
        response = self.client.get(reverse("admin:market_inventory_add"))
        self.assertTrue(response.context_data.get("confirm_change"))
        self.assertIn("_confirm_change", response.rendered_content)

    def test_post_add_without_confirm_add(self):
        data = {"name": "name", "price": 2.0, "currency": Item.VALID_CURRENCIES[0]}
        response = self.client.post(reverse("admin:market_item_add"), data)
        # Redirects to item changelist and item is added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/item/")
        self.assertEqual(Item.objects.count(), 1)

    def test_post_add_with_confirm_add(self):
        item = ItemFactory()
        shop = ShopFactory()
        data = {
            "shop": shop.id,
            "item": item.id,
            "quantity": 5,
            "_confirm_add": True,
            "_continue": True,
        }
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
        self._assertSimpleFieldFormHtml(
            rendered_content=response.rendered_content, fields=form_data
        )
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Should not have been added yet
        self.assertEqual(Inventory.objects.count(), 0)

    def test_post_change_with_confirm_change_shoppingmall_name(self):
        # When testing found that even though name was in confirmation_fields
        # When only name changed, `form.is_valid` = False, and thus didn't trigger
        # confirmation page previously, even though it should have

        mall = ShoppingMall.objects.create(name="name")
        data = {
            "id": mall.id,
            "name": "new name",
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/", data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/shoppingmall/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Hasn't changed item yet
        mall.refresh_from_db()
        self.assertEqual(mall.name, "name")

    def test_post_change_with_confirm_change(self):
        item = ItemFactory(name="item")
        data = {
            "name": "name",
            "price": 2.0,
            "currency": Item.VALID_CURRENCIES[0],
            "id": item.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(f"/admin/market/item/{item.id}/change/", data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/item/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = {
            "name": "name",
            "price": str(2.0),
            # "id": str(item.id),
            "currency": Item.VALID_CURRENCIES[0][0],
        }

        self._assertSimpleFieldFormHtml(
            rendered_content=response.rendered_content, fields=form_data
        )
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, multipart_form=True
        )

        # Hasn't changed item yet
        item.refresh_from_db()
        self.assertEqual(item.name, "item")

    def test_post_change_without_confirm_change(self):
        shop = ShopFactory(name="bob")
        data = {"name": "sally"}
        response = self.client.post(f"/admin/market/shop/{shop.id}/change/", data)
        # Redirects to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shop/")
        # Shop has changed
        shop.refresh_from_db()
        self.assertEqual(shop.name, "sally")

    def test_get_confirmation_fields_should_default_if_not_set(self):
        expected_fields = [f.name for f in Item._meta.fields if f.name != "id"]
        ItemAdmin.confirmation_fields = None
        ItemAdmin.fields = expected_fields
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(self.factory.request())
        for field in expected_fields:
            self.assertIn(field, actual_fields)

    def test_get_confirmation_fields_default_should_only_include_fields_shown_on_admin(
        self,
    ):
        admin_fields = ["name", "price"]
        ItemAdmin.confirmation_fields = None
        ItemAdmin.fields = admin_fields
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(self.factory.request())
        for field in admin_fields:
            self.assertIn(field, actual_fields)

    def test_get_confirmation_fields_if_set(self):
        expected_fields = ["name", "currency"]
        ItemAdmin.confirmation_fields = expected_fields
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(self.factory.request())
        self.assertEqual(expected_fields, actual_fields)

    def test_custom_template(self):
        expected_template = "market/admin/my_custom_template.html"
        ItemAdmin.change_confirmation_template = expected_template
        admin = ItemAdmin(Item, AdminSite())
        actual_template = admin.render_change_confirmation(
            self.factory.request(), context={}
        ).template_name
        self.assertEqual(expected_template, actual_template)
        # Clear our setting to not affect other tests
        ItemAdmin.change_confirmation_template = None

    def test_form_invalid(self):
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

    def test_confirmation_fields_set_with_confirm_change(self):
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

    def test_confirmation_fields_set_with_confirm_add(self):
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

    def test_no_change_permissions(self):
        user = User.objects.create_user(username="user", is_staff=True)
        self.client.force_login(user)

        inventory = InventoryFactory()
        data = {
            "quantity": 1000,
            "id": inventory.id,
            "item": inventory.item.id,
            "shop": inventory.shop.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
        }
        response = self.client.post(
            f"/admin/market/inventory/{inventory.id}/change/", data
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(isinstance(response, HttpResponseForbidden))

        old_quantity = inventory.quantity
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, old_quantity)

    def test_no_add_permissions(self):
        user = User.objects.create_user(username="user", is_staff=True)
        self.client.force_login(user)
        item = ItemFactory()
        shop = ShopFactory()
        data = {"shop": shop.id, "item": item.id, "quantity": 5, "_confirm_add": True}
        response = self.client.post(reverse("admin:market_inventory_add"), data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(isinstance(response, HttpResponseForbidden))

        # Should not have been added
        self.assertEqual(Inventory.objects.count(), 0)

    def test_obj_not_found(self):
        inventory = InventoryFactory()
        data = {
            "quantity": 1000,
            "id": 100,
            "item": inventory.item.id,
            "shop": inventory.shop.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
        }
        response = self.client.post("/admin/market/inventory/100/change/", data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")
        self.assertEqual(response.reason_phrase, "Found")

        old_quantity = inventory.quantity
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, old_quantity)

        self.assertEqual(Inventory.objects.count(), 1)

    def test_handles_to_field_not_allowed(self):
        item = ItemFactory()
        shop = ShopFactory()
        data = {
            "shop": shop.id,
            "item": item.id,
            "quantity": 5,
            "_confirm_add": True,
            TO_FIELD_VAR: "shop",
        }
        response = self.client.post(reverse("admin:market_inventory_add"), data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))
        self.assertEqual(response.reason_phrase, "Bad Request")
        self.assertEqual(
            response.context.get("exception_value"),
            "The field shop cannot be referenced.",
        )

        # Should not have been added
        self.assertEqual(Inventory.objects.count(), 0)
