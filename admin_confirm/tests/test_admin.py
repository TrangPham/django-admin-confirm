from unittest import mock
from requests import Request
from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from tests.market.admin import ItemAdmin, InventoryAdmin, ShopAdmin
from tests.market.models import Item
from tests.factories import ItemFactory, InventoryFactory, ShopFactory


class TestAdminConfirmMixin(TestCase):
    @mock.patch('django.contrib.admin.options.changeform_view')
    def test_add_without_confirm(self, mock_super):
        ItemAdmin.confirm_add = None
        admin = ItemAdmin(Item, AdminSite())
        request = Request('POST', 'url', data={'name': 'name', 'price': 2.0, 'currency': Item.VALID_CURRENCIES[0]})

        confirmation_template = admin.render_change_confirmation(request, context={}).template_name
        # object_id = None for adding
        actual_template = admin.changeform_view(request).template_name
        mock_super.assert_called_once()
        self.assertNotEqual(confirmation_template, actual_template)

    def test_change_with_no_options(self):


    def test_with_confirm_change(self):
        pass

    def test_with_confirm_add(self):
        pass

    def test_get_confirmation_fields_should_default_if_not_set(self):
        expected_fields = [f.name for f in Item._meta.fields if f.name != 'id']
        ItemAdmin.confirmation_fields = None
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(Request('GET', 'url'))
        self.assertEqual(expected_fields, actual_fields)

    def test_get_confirmation_fields_if_set(self):
        expected_fields = ['name', 'currency']
        ItemAdmin.confirmation_fields = expected_fields
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(Request('GET', 'url'))
        self.assertEqual(expected_fields, actual_fields)

    def test_custom_template(self):
        expected_template = 'my_custom_template.html'
        ItemAdmin.confirmation_template = expected_template
        admin = ItemAdmin(Item, AdminSite())
        actual_template = admin.render_change_confirmation(Request('POST', 'url'), context={}).template_name
        self.assertEqual(expected_template, actual_template)



class TestAdminConfirmMixinConfirmChange(TestCase):
    pass


class TestAdminConfirmMixinConfirmAdd(TestCase):
    pass


class TestAdminConfirmMixinConfirmChangeWithFields(TestCase):
    pass


class TestAdminConfirmMixinConfirmChangeWithFields(TestCase):
    pass