"""
Tests confirmation of add/change
on ModelAdmin that includes inlines

Does not test confirmation of inline changes
"""

import pytest
import django
from importlib import reload
from tests.factories import ShopFactory
from tests.market.models import GeneralManager, ShoppingMall, Town

from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase
from tests.market.admin import shoppingmall_admin

from admin_confirm.constants import CONFIRM_ADD, CONFIRM_CHANGE
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class ConfirmWithInlinesTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.admin = shoppingmall_admin.ShoppingMallAdmin
        super().setUp()
        self.setAdminAttributes(
            shoppingmall_admin.ShoppingMallAdmin,
            inlines=[shoppingmall_admin.ShopInline],
        )

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_should_have_hidden_form(self):
        mall = ShoppingMall.objects.create(name="mall")
        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
        # Should ask for confirmation of change
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Change name
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should have hidden form containing the updated name
        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        name = hidden_form.find_element(By.NAME, "name")
        self.assertIn("New Name", name.get_attribute("value"))

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should persist change
        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)

    def test_should_have_hidden_formsets(self):
        # Not having formsets would cause a `ManagementForm tampered with` issue
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory(name=i) for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("This is New Name")

        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        hidden_form.find_element(By.NAME, "ShoppingMall_shops-TOTAL_FORMS")

        self.selenium.find_element(By.NAME, "_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)

    def test_should_have_saved_inline_changes(self):
        gm = GeneralManager.objects.create(name="gm")
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)

        shops = [ShopFactory(name=i) for i in range(3)]

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        # Change shops via inline form
        select_shop = Select(self.selenium.find_element(By.NAME, "ShoppingMall_shops-0-shop"))
        select_shop.select_by_value(str(shops[2].id))

        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        hidden_form.find_element(By.NAME, "ShoppingMall_shops-TOTAL_FORMS")
        self.selenium.find_element(By.NAME, "_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)
        self.assertIn(shops[2], mall.shops.all())

    def test_should_respect_get_inlines(self):
        # New in Django 3.0
        django_major = django.VERSION[0]
        if django_major < 3:
            pytest.skip("get_inlines() introducted in Django 3.0, and is not in this version")

        shoppingmall_admin.ShoppingMallAdmin.inlines = []
        shoppingmall_admin.ShoppingMallAdmin.get_inlines = lambda self, request, obj=None: [
            shoppingmall_admin.ShopInline
        ]

        gm = GeneralManager.objects.create(name="gm")
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)

        shops = [ShopFactory(name=i) for i in range(3)]

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        # Change shops via inline form
        select_shop = Select(self.selenium.find_element(By.NAME, "ShoppingMall_shops-0-shop"))
        select_shop.select_by_value(str(shops[2].id))

        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        hidden_form.find_element(By.NAME, "ShoppingMall_shops-TOTAL_FORMS")
        self.selenium.find_element(By.NAME, "_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)
        self.assertIn(shops[2], mall.shops.all())

    def test_should_respect_get_inline_instances(self):
        shoppingmall_admin.ShoppingMallAdmin.inlines = []
        shoppingmall_admin.ShoppingMallAdmin.get_inline_instances = (
            lambda self, request, obj=None: shoppingmall_admin.ShopInline(
                self.model, self.admin_site
            )
        )
        gm = GeneralManager.objects.create(name="gm")
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)

        shops = [ShopFactory(name=i) for i in range(3)]

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/{mall.id}/change/")
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Make a change to trigger confirmation page
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("New Name")

        # Change shops via inline form
        select_shop = Select(self.selenium.find_element(By.NAME, "ShoppingMall_shops-0-shop"))
        select_shop.select_by_value(str(shops[2].id))

        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertIn("Confirm", self.selenium.page_source)

        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        hidden_form.find_element(By.NAME, "ShoppingMall_shops-TOTAL_FORMS")
        self.selenium.find_element(By.NAME, "_continue").click()

        mall.refresh_from_db()
        self.assertIn("New Name", mall.name)
        self.assertIn(shops[2], mall.shops.all())

    def test_detects_changes_to_m2m_fields(self):
        # make the m2m the only confirmation_field
        self.setAdminAttributes(shoppingmall_admin.ShoppingMallAdmin, confirmation_fields=["shops"])
        shops = [ShopFactory() for i in range(3)]
        shopping_mall = ShoppingMall.objects.create(name="name")
        shopping_mall.refresh_from_db()
        assert shopping_mall.shops.count() == 0

        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{shopping_mall.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Click on one of the shops in the m2m field to change it
        select_shop = Select(self.selenium.find_element(By.NAME, "shops"))
        select_shop.select_by_value(str(shops[0].id))

        # Click save and continue to trigger confirmation page
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should ask for confirmation since m2m field has changed
        self.assertIn("Confirm", self.selenium.page_source)

        # Shops has not changed until confirmation received
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.shops.count(), 0)

        # Click on "Yes, I'm sure" to confirm change
        self.selenium.find_element(By.NAME, "_continue").click()

        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.shops.count(), 1)
        self.assertIn(shops[0], shopping_mall.shops.all())

    def test_change_does_not_trigger_confirmation_if_m2m_field_in_confirmation_fields_but_m2m_field_not_changed(
        self,
    ):
        # make the m2m the only confirmation_field
        self.setAdminAttributes(shoppingmall_admin.ShoppingMallAdmin, confirmation_fields=["shops"])
        shops = [ShopFactory() for i in range(3)]
        shopping_mall = ShoppingMall.objects.create(name="name")
        shopping_mall.shops.set(shops)
        shopping_mall.refresh_from_db()
        assert shopping_mall.shops.count() == 3

        self.selenium.get(
            self.live_server_url + f"/admin/market/shoppingmall/{shopping_mall.id}/change/"
        )
        self.assertIn(CONFIRM_CHANGE, self.selenium.page_source)

        # Do nothing and submit form
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should not ask for confirmation since m2m field has not changed
        self.assertNotIn("Confirm", self.selenium.page_source)

        # Shops has not changed
        shopping_mall.refresh_from_db()
        self.assertEqual(shopping_mall.shops.count(), 3)

    def test_add_does_not_trigger_confirmation_if_m2m_field_in_confirmation_fields_but_m2m_field_not_changed(
        self,
    ):
        # make the m2m the only confirmation_field
        self.setAdminAttributes(shoppingmall_admin.ShoppingMallAdmin, confirmation_fields=["shops"])

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/add/")
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        # Fill in required fields, but do not change m2m field
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("name")
        self.selenium.find_element(By.NAME, "_continue").click()

        # Should not ask for confirmation since m2m field has not changed
        self.assertNotIn("Confirm", self.selenium.page_source)

    def test_add_does_trigger_confirmation_if_m2m_field_in_confirmation_fields_and_changed_from_default(
        self,
    ):
        # make the m2m the only confirmation_field
        self.setAdminAttributes(shoppingmall_admin.ShoppingMallAdmin, confirmation_fields=["shops"])
        shops = [ShopFactory() for i in range(3)]

        self.selenium.get(self.live_server_url + f"/admin/market/shoppingmall/add/")
        self.assertIn(CONFIRM_ADD, self.selenium.page_source)

        # Fill in required fields
        name = self.selenium.find_element(By.NAME, "name")
        name.send_keys("name")

        # Select a shop in the m2m field to change it from the default of empty
        select_shop = Select(self.selenium.find_element(By.NAME, "shops"))
        select_shop.select_by_value(str(shops[0].id))

        self.selenium.find_element(By.NAME, "_continue").click()

        # Should ask for confirmation since m2m field has changed from default
        self.assertIn("Confirm", self.selenium.page_source)
