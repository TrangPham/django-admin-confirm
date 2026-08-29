import pytest
from unittest import mock

from django.urls import reverse
from django.contrib.admin import ModelAdmin

from admin_confirm.admin import AdminConfirmMixin, confirm_action
from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.models import ShoppingMall, Shop
from tests.factories import ShopFactory

from tests.market.admin import ShoppingMallAdmin, ShopAdmin


@mock.patch.object(ShoppingMallAdmin, "inlines", [])
class TestCustomConfirmationMessage(AdminConfirmTestCase):
    """
    Customization of the confirmation page message via the
    get_add_confirmation_message / get_change_confirmation_message /
    get_action_confirmation_message hooks.
    """

    # ─── Add ───

    def test_add_confirmation_default_message(self):
        data = {"name": "name", "_confirm_add": True, "_save": True}
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Are you sure you want to add", response.rendered_content)

    def test_add_confirmation_custom_message(self):
        self.setAdminAttributes(
            ShoppingMallAdmin,
            get_add_confirmation_message=lambda self, request, obj=None: "Custom add message",
        )
        data = {"name": "name", "_confirm_add": True, "_save": True}
        response = self.client.post(reverse("admin:market_shoppingmall_add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Custom add message", response.rendered_content)
        self.assertNotIn("Are you sure you want to add", response.rendered_content)

    # ─── Change ───

    def test_change_confirmation_default_message(self):
        mall = ShoppingMall.objects.create(name="name")
        data = {
            "id": mall.id,
            "name": "new name",
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Are you sure you want to change", response.rendered_content)

    def test_change_confirmation_custom_message(self):
        def custom_change_message(self, request, obj=None, changed_data=None):
            return f"Custom change message for {obj} fields {sorted(changed_data.keys())}"

        self.setAdminAttributes(ShoppingMallAdmin, get_change_confirmation_message=custom_change_message)
        mall = ShoppingMall.objects.create(name="name")
        data = {
            "id": mall.id,
            "name": "new name",
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_save": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Custom change message for", response.rendered_content)
        self.assertIn("name", response.rendered_content)
        self.assertNotIn("Are you sure you want to change", response.rendered_content)

    # ─── Action ───

    def test_action_confirmation_default_message(self):
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            {
                "action": "show_message",
                "_selected_action": [1],
                "csrfmiddlewaretoken": "fake token",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Are you sure you want to perform action", response.rendered_content)

    def test_action_confirmation_custom_message(self):
        self.setAdminAttributes(
            ShopAdmin,
            get_action_confirmation_message=lambda self, request, queryset: "Custom action message",
        )
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            {
                "action": "show_message",
                "_selected_action": [1],
                "csrfmiddlewaretoken": "fake token",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Custom action message", response.rendered_content)
        self.assertNotIn("Are you sure you want to perform action", response.rendered_content)
