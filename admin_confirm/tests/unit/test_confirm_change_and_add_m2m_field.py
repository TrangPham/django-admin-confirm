from unittest import mock
from admin_confirm.admin import AdminConfirmMixin
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.admin import ShoppingMallAdmin
from tests.market.models import ShoppingMall
from tests.factories import ShopFactory


@mock.patch.object(ShoppingMallAdmin, "inlines", [])
class TestConfirmChangeAndAddM2MField(AdminConfirmTestCase):
    def test_post_add_without_confirm_add_m2m(self):
        shops = [ShopFactory() for i in range(3)]

        data = {"name": "name", "shops": [s.id for s in shops]}
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data)
        # Redirects to changelist and is added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shoppingmall/")
        self.assertEqual(ShoppingMall.objects.count(), 1)
        self.assertEqual(ShoppingMall.objects.all().first().shops.count(), 3)

    def test_post_add_with_confirm_add_m2m(self):
        ShoppingMallAdmin.confirmation_fields = ["shops"]
        shops = [ShopFactory() for i in range(3)]

        data = {
            "name": "name",
            "shops": [s.id for s in shops],
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/shoppingmall/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertManyToManyFormHtml(
            rendered_content=response.rendered_content,
            options=shops,
            selected_ids=data["shops"],
        )
        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Should not have been added yet
        self.assertEqual(ShoppingMall.objects.count(), 0)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shoppingmall/")
        self.assertEqual(ShoppingMall.objects.count(), 1)
        self.assertEqual(ShoppingMall.objects.all().first().shops.count(), 3)

    def test_m2m_field_post_change_with_confirm_change(self):
        shops = [ShopFactory() for i in range(10)]
        shopping_mall = ShoppingMall.objects.create(name="My Mall")
        shopping_mall.shops.set(shops)
        # Currently ShoppingMall configured with confirmation_fields = ['name']
        data = {
            "name": "Not My Mall",
            "shops": [1, 2],
            "id": shopping_mall.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_continue": True,
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

        # Should show two lists for the m2m current and modified values
        self.assertEqual(response.rendered_content.count("<ul>"), 2)

        self._assertManyToManyFormHtml(
            rendered_content=response.rendered_content,
            options=shops,
            selected_ids=data["shops"],
        )
        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Hasn't changed item yet
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.name, "My Mall")

        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        del data["_confirm_change"]
        response = self.client.post(
            f"/admin/market/shoppingmall/{shopping_mall.id}/change/", data
        )
        # will show the change page for this shopping_mall
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/admin/market/shoppingmall/{shopping_mall.id}/change/"
        )
        # Should not be the confirmation page, we already confirmed change
        self.assertNotEqual(response.templates, expected_templates)
        self.assertEqual(ShoppingMall.objects.count(), 1)
        self.assertEqual(ShoppingMall.objects.all().first().shops.count(), 2)

    def test_m2m_field_post_change_with_confirm_change_multiple_selected(self):
        shops = [ShopFactory() for i in range(10)]
        shopping_mall = ShoppingMall.objects.create(name="My Mall")
        shopping_mall.shops.set(shops)
        # Currently ShoppingMall configured with confirmation_fields = ['name']
        data = {
            "name": "Not My Mall",
            "shops": [1, 2, 3],
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

        # Hasn't changed item yet
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.name, "My Mall")

    def test_post_change_without_confirm_change_m2m_value(self):
        # make the m2m the confirmation_field
        ShoppingMallAdmin.confirmation_fields = ["shops"]
        shops = [ShopFactory() for i in range(3)]
        shopping_mall = ShoppingMall.objects.create(name="name")
        shopping_mall.shops.set(shops)
        assert shopping_mall.shops.count() == 3

        data = {"name": "name", "id": str(shopping_mall.id), "shops": ["1"]}
        response = self.client.post(
            f"/admin/market/shoppingmall/{shopping_mall.id}/change/", data
        )
        # Redirects to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/shoppingmall/")
        # Shop has changed
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.shops.count(), 1)

    def test_form_invalid_m2m_value(self):
        ShoppingMallAdmin.confirmation_fields = ["shops"]
        shopping_mall = ShoppingMall.objects.create(name="name")

        data = {
            "id": shopping_mall.id,
            "name": "name",
            "shops": [1, 2, 3],  # These shops don't exist
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
        }
        response = self.client.post(
            f"/admin/market/shoppingmall/{shopping_mall.id}/change/", data
        )

        # Form invalid should show errors on form
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data.get("errors"))
        self.assertTrue(
            str(response.context_data["errors"][0][0]).startswith(
                "Select a valid choice."
            )
        )
        # Should not have updated inventory
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.shops.count(), 0)
