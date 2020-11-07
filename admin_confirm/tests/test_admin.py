from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite

from tests.market.admin import ItemAdmin
from tests.market.models import Item, Inventory
from django.urls import reverse
from tests.factories import ItemFactory, ShopFactory


class TestAdminConfirmMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='super', email='super@email.org', password='pass')

    def setUp(self):
        self.client.force_login(self.superuser)
        self.factory = RequestFactory()

    def test_get_add_without_confirm_add(self):
        response = self.client.get(reverse('admin:market_item_add'))
        self.assertFalse(response.context_data.get('confirm_add'))
        self.assertNotIn('_confirm_add', response.rendered_content)

    def test_get_add_with_confirm_add(self):
        response = self.client.get(reverse('admin:market_inventory_add'))
        self.assertTrue(response.context_data.get('confirm_add'))
        self.assertIn('_confirm_add', response.rendered_content)

    def test_get_change_without_confirm_change(self):
        response = self.client.get(reverse('admin:market_shop_add'))
        self.assertFalse(response.context_data.get('confirm_change'))
        self.assertNotIn('_confirm_change', response.rendered_content)

    def test_get_change_with_confirm_change(self):
        response = self.client.get(reverse('admin:market_inventory_add'))
        self.assertTrue(response.context_data.get('confirm_change'))
        self.assertIn('_confirm_change', response.rendered_content)

    def test_post_add_without_confirm_add(self):
        data = {'name': 'name', 'price': 2.0,
                'currency': Item.VALID_CURRENCIES[0]}
        response = self.client.post(reverse('admin:market_item_add'), data)
        # Redirects to item changelist and item is added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/market/item/')
        self.assertEqual(Item.objects.count(), 1)

    def test_post_add_with_confirm_add(self):
        item = ItemFactory()
        shop = ShopFactory()
        data = {'shop': shop.id, 'item': item.id,
                'quantity': 5, '_confirm_add': True}
        response = self.client.post(
            reverse('admin:market_inventory_add'), data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'admin/market/inventory/change_confirmation.html',
            'admin/market/change_confirmation.html',
            'admin/change_confirmation.html'
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = {'shop': str(shop.id), 'item': str(
            item.id), 'quantity': str(5)}
        self.assertEqual(
            response.context_data['form_data'], form_data)
        for k, v in form_data.items():
            self.assertIn(
                f'<input type="hidden" name="{ k }" value="{ v }">', response.rendered_content)

        # Should not have been added yet
        self.assertEqual(Inventory.objects.count(), 0)

    def test_post_change_with_confirm_change(self):
        item = ItemFactory(name='item')
        data = {'name': 'name', 'price': 2.0,
                'currency': Item.VALID_CURRENCIES[0], '_confirm_change': True}
        response = self.client.post(
            f'/admin/market/item/{item.id}/change/', data)
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'admin/market/item/change_confirmation.html',
            'admin/market/change_confirmation.html',
            'admin/change_confirmation.html'
        ]
        self.assertEqual(response.template_name, expected_templates)
        form_data = {'name': 'name', 'price': str(2.0),
                     'currency': Item.VALID_CURRENCIES[0][0]}
        self.assertEqual(
            response.context_data['form_data'], form_data)
        for k, v in form_data.items():
            self.assertIn(
                f'<input type="hidden" name="{ k }" value="{ v }">', response.rendered_content)

        # Hasn't changed item yet
        item.refresh_from_db()
        self.assertEqual(item.name, 'item')

    def test_post_change_without_confirm_change(self):
        shop = ShopFactory(name='bob')
        data = {'name': 'sally'}
        response = self.client.post(
            f'/admin/market/shop/{shop.id}/change/', data)
        # Redirects to changelist
        print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/market/shop/')
        # Shop has changed
        shop.refresh_from_db()
        self.assertEqual(shop.name, 'sally')

    def test_get_confirmation_fields_should_default_if_not_set(self):
        expected_fields = [f.name for f in Item._meta.fields if f.name != 'id']
        ItemAdmin.confirmation_fields = None
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(self.factory.request())
        self.assertEqual(expected_fields, actual_fields)

    def test_get_confirmation_fields_if_set(self):
        expected_fields = ['name', 'currency']
        ItemAdmin.confirmation_fields = expected_fields
        admin = ItemAdmin(Item, AdminSite())
        actual_fields = admin.get_confirmation_fields(self.factory.request())
        self.assertEqual(expected_fields, actual_fields)

    def test_custom_template(self):
        expected_template = 'market/admin/my_custom_template.html'
        ItemAdmin.confirmation_template = expected_template
        admin = ItemAdmin(Item, AdminSite())
        actual_template = admin.render_change_confirmation(
            self.factory.request(), context={}).template_name
        self.assertEqual(expected_template, actual_template)
        ItemAdmin.confirmation_template = None
