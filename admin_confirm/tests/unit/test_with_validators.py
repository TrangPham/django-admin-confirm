"""
Ensures that confirmations work with validators on the Model and on the Modelform.
"""

from unittest import mock
from django.urls import reverse

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.models import ItemSale
from tests.factories import (
    InventoryFactory,
    ItemFactory,
    ShopFactory,
    TransactionFactory,
)


class TestWithValidators(AdminConfirmTestCase):
    @mock.patch("tests.market.models.ItemSale.clean")
    def test_can_confirm_for_models_with_validator_on_model_field(self, _mock_clean):
        # ItemSale.currency has a validator on it
        item = ItemFactory()
        transaction = TransactionFactory()
        data = {
            "transaction": transaction.id,
            "item": item.id,
            "quantity": 1,
            "currency": "USD",
            "total": 10.00,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_itemsale_add"), data)

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_itemsale_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/itemsale/")
        self.assertEqual(ItemSale.objects.count(), 1)

        # Ensure that the date and timestamp saved correctly
        item_sale = ItemSale.objects.first()
        self.assertEqual(item_sale.transaction, transaction)
        self.assertEqual(item_sale.item, item)
        self.assertEqual(item_sale.currency, "USD")

    def test_cannot_confirm_for_models_with_validator_on_model_field_if_validator_fails(
        self,
    ):
        # ItemSale.currency has a validator on it
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=10)
        transaction = TransactionFactory(shop=shop)
        data = {
            "transaction": transaction.id,
            "item": item.id,
            "quantity": 1,
            "currency": "FAKE",
            "total": 10.00,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_itemsale_add"), data)
        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_itemsale_add"), data)

        # Should not have redirected, since there was an error
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_form.html",
            "admin/market/change_form.html",
            "admin/change_form.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self.assertEqual(ItemSale.objects.count(), 0)
        self.assertTrue("error" in str(response.content))
        self.assertTrue("Invalid Currency" in str(response.content))

    def test_can_confirm_for_models_with_clean_overridden(self):
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=10)
        transaction = TransactionFactory(shop=shop)
        data = {
            "transaction": transaction.id,
            "item": item.id,
            "quantity": 9,
            "currency": "USD",
            "total": 10.00,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_itemsale_add"), data)

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_itemsale_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/itemsale/")
        self.assertEqual(ItemSale.objects.count(), 1)

        # Ensure that the date and timestamp saved correctly
        item_sale = ItemSale.objects.first()
        self.assertEqual(item_sale.transaction, transaction)
        self.assertEqual(item_sale.item, item)
        self.assertEqual(item_sale.currency, "USD")

    def test_cannot_confirm_for_models_with_clean_overridden_if_clean_fails(self):
        shop = ShopFactory()
        item = ItemFactory()
        InventoryFactory(shop=shop, item=item, quantity=1)
        transaction = TransactionFactory(shop=shop)
        data = {
            "transaction": transaction.id,
            "item": item.id,
            "quantity": 9,
            "currency": "USD",
            "total": 10.00,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_itemsale_add"), data)

        # Should not have been added yet
        self.assertEqual(ItemSale.objects.count(), 0)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_itemsale_add"), data)

        # Should not have redirected, since there was an error
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/itemsale/change_form.html",
            "admin/market/change_form.html",
            "admin/change_form.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self.assertEqual(ItemSale.objects.count(), 0)
        self.assertTrue("error" in str(response.content))
        self.assertTrue(
            "Shop does not have enough of the item stocked" in str(response.content)
        )

    def test_can_confirm_for_modelform_with_clean_field_overridden(self):
        pass

    def test_can_confirm_for_modelform_with_clean_overridden(self):
        pass
