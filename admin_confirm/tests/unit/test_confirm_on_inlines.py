from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponseForbidden
from django.urls import reverse

from admin_confirm.constants import CONFIRMATION_OPTIONS
from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.models import Consumer, Transaction
from tests.market.admin.consumer_admin import ConsumerAdmin, TransactionInline
from tests.factories import (
    ShopFactory,
    ConsumerFactory,
    TransactionFactory,
)


class TestConfirmOnInlines(AdminConfirmTestCase):
    def setUp(self):
        super().setUp()
        self.setAdminAttributes(
            ConsumerAdmin,
            # Inline confirmations do not require parent admin to require confirmation.
            confirm_change=False,
            confirm_add=False,
            confirmation_fields=["name"],
            inlines=[TransactionInline],
        )
        self.consumer = ConsumerFactory(name="bob")
        self.shop = ShopFactory(name="shop")
        self.transaction = TransactionFactory.build(
            consumer=self.consumer,
            shop=self.shop,
        )

        # For inline get_confirmation_fields,
        # has_delete_permissions is checked by underlying Django code, which requires a request with a user.
        self.request = self.factory.post("/")
        self.request.user = self.superuser

    def test_get_add_inline_without_confirm_add(self):
        self.setAdminAttributes(TransactionInline, confirm_add=False)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))

        # Parent does not require confirm add
        self.assertNotIn("_confirm_add", response.context_data.get(CONFIRMATION_OPTIONS))
        self.assertNotIn("_confirm_add", response.rendered_content)

        # Inline does not require confirm add
        prefix = f"{TransactionInline.model.__name__}"
        self.assertNotIn(f"{prefix}_confirm_add", response.context_data.get(CONFIRMATION_OPTIONS))
        self.assertNotIn(f"{prefix}_confirm_add", response.rendered_content)

    def test_get_add_inline_with_confirm_add(self):
        self.setAdminAttributes(TransactionInline, confirm_add=True)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))
        prefix = f"{TransactionInline.model.__name__}"
        self.assertIn(f"{prefix}_confirm_add", response.context_data.get(CONFIRMATION_OPTIONS))
        self.assertIn(f"{prefix}_confirm_add", response.rendered_content)

    def test_get_change_inline_without_confirm_change(self):
        self.setAdminAttributes(TransactionInline, confirm_change=False)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))
        prefix = f"{TransactionInline.model.__name__}"
        self.assertNotIn(
            f"{prefix}_confirm_change", response.context_data.get(CONFIRMATION_OPTIONS)
        )
        self.assertNotIn(f"{prefix}_confirm_change", response.rendered_content)

    def test_get_change_inline_with_confirm_change(self):
        self.setAdminAttributes(TransactionInline, confirm_change=True)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))
        prefix = f"{TransactionInline.model.__name__}"
        self.assertIn(f"{prefix}_confirm_change", response.context_data.get(CONFIRMATION_OPTIONS))
        self.assertIn(f"{prefix}_confirm_change", response.rendered_content)

    def test_get_delete_inline_without_confirm_delete(self):
        self.setAdminAttributes(TransactionInline, confirm_delete=False)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))
        prefix = f"{TransactionInline.model.__name__}"
        self.assertNotIn(
            f"{prefix}_confirm_delete", response.context_data.get(CONFIRMATION_OPTIONS)
        )
        self.assertNotIn(f"{prefix}_confirm_delete", response.rendered_content)

    def test_get_delete_inline_with_confirm_delete(self):
        self.setAdminAttributes(TransactionInline, confirm_delete=True)
        response = self.client.get(reverse("admin:market_consumer_change", args=[self.consumer.id]))
        prefix = f"{TransactionInline.model.__name__}"
        self.assertIn(f"{prefix}_confirm_delete", response.context_data.get(CONFIRMATION_OPTIONS))
        self.assertIn(f"{prefix}_confirm_delete", response.rendered_content)

    def test_post_add_inline_without_confirm_add(self):
        self.setAdminAttributes(TransactionInline, confirm_add=False)
        data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "0",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": "",
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": str(self.transaction.total),
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Redirects to consumer changelist and transaction is added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/consumer/")
        self.assertEqual(Transaction.objects.count(), 1)
        created_transaction = Transaction.objects.first()
        self.assertEqual(created_transaction.consumer, self.consumer)
        self.assertEqual(created_transaction.shop, self.shop)

    def test_post_add_inline_with_confirm_add(self):
        self.setAdminAttributes(TransactionInline, confirm_add=True)
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "0",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": "",
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": str(self.transaction.total),
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "Transaction_confirm_add": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/consumer/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self._assertSimpleFieldFormHtml(
            rendered_content=response.rendered_content, fields=form_data
        )
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_save")

        # Should not have been added yet
        self.assertEqual(Transaction.objects.count(), 0)

    def test_post_inline_change_with_confirm_change(self):
        self.setAdminAttributes(TransactionInline, confirm_change=True)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "Transaction_confirm_change": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/consumer/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self._assertSimpleFieldFormHtml(
            rendered_content=response.rendered_content, fields=form_data
        )
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_save")

        # Hasn't changed yet
        self.transaction.refresh_from_db()
        self.assertNotEqual(self.transaction.total, 999.00)

    def test_post_inline_change_without_confirm_change(self):
        self.setAdminAttributes(TransactionInline, confirm_change=False)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Redirects to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/consumer/")
        # Transaction has been updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.total, 999.00)

    def test_post_inline_delete_with_confirm_delete(self):
        self.setAdminAttributes(TransactionInline, confirm_delete=True)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "transactions-0-DELETE": True,
            "Transaction_confirm_delete": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/consumer/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)
        self._assertSimpleFieldFormHtml(
            rendered_content=response.rendered_content, fields=form_data
        )
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_save")

        # Transaction not changed
        self.transaction.refresh_from_db()
        self.assertNotEqual(self.transaction.total, 999.00)
        # Nor should it have been deleted
        self.assertEqual(Transaction.objects.count(), 1)

    def test_post_inline_delete_without_confirm_delete(self):
        self.setAdminAttributes(TransactionInline, confirm_delete=False)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "transactions-0-DELETE": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Redirects to changelist
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/consumer/")
        # Transaction has been deleted
        self.assertEqual(Transaction.objects.count(), 0)

    def test_get_confirmation_fields_respects___all__for_inline(self):
        expected_fields = [f.name for f in Transaction._meta.fields if f.name != "id"]
        self.setAdminAttributes(TransactionInline, confirmation_fields="__all__")
        self.setAdminAttributes(ConsumerAdmin, inlines=[TransactionInline])
        site = AdminSite()
        admin = ConsumerAdmin(Consumer, site)
        inline = admin.inlines[0](Consumer, site)

        actual_fields = inline.get_confirmation_fields(self.request)
        for field in expected_fields:
            self.assertIn(field, actual_fields)

    def test_get_confirmation_fields_should_default_if_not_set(self):
        expected_fields = [f.name for f in Transaction._meta.fields if f.name != "id"]
        self.setAdminAttributes(TransactionInline, confirmation_fields=None)
        self.setAdminAttributes(ConsumerAdmin, inlines=[TransactionInline])
        site = AdminSite()
        admin = ConsumerAdmin(Consumer, site)
        inline = admin.inlines[0](Consumer, site)

        actual_fields = inline.get_confirmation_fields(self.request)
        for field in expected_fields:
            self.assertIn(field, actual_fields)

    def test_get_confirmation_fields_default_should_only_include_fields_shown_on_admin(
        self,
    ):
        admin_fields = ["total", "currency"]
        self.setAdminAttributes(TransactionInline, confirmation_fields=None, fields=admin_fields)
        self.setAdminAttributes(ConsumerAdmin, inlines=[TransactionInline])
        site = AdminSite()
        admin = ConsumerAdmin(Consumer, site)
        inline = admin.inlines[0](Consumer, site)

        actual_fields = inline.get_confirmation_fields(self.request)
        self.assertCountEqual(admin_fields, actual_fields)

    def test_get_confirmation_fields_if_set(self):
        expected_fields = ["total", "currency"]
        self.setAdminAttributes(TransactionInline, confirmation_fields=expected_fields)
        self.setAdminAttributes(ConsumerAdmin, inlines=[TransactionInline])
        site = AdminSite()
        admin = ConsumerAdmin(Consumer, site)
        inline = admin.inlines[0](Consumer, site)

        actual_fields = inline.get_confirmation_fields(self.request)
        self.assertCountEqual(expected_fields, actual_fields)

    def test_get_confirmation_fields_if_set_with_invalid_field(self):
        expected_fields = ["total", "currency"]
        self.setAdminAttributes(
            TransactionInline, confirmation_fields=expected_fields + ["invalid_field"]
        )
        self.setAdminAttributes(ConsumerAdmin, inlines=[TransactionInline])
        site = AdminSite()
        admin = ConsumerAdmin(Consumer, site)
        inline = admin.inlines[0](Consumer, site)

        actual_fields = inline.get_confirmation_fields(self.request)
        self.assertCountEqual(expected_fields, actual_fields)

    def test_multiple_inline_rows_form_invalid(self):
        # Note: Testing inlines with integration tests can be tricky as some inline html elements are generated by JavaScript
        # and not present in the initial HTML response. Instead simulating the form submission process with POST request sequence.
        self.setAdminAttributes(TransactionInline, confirm_change=True)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "2",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
            "transactions-1-id": "",
            "transactions-1-consumer": "invalid",
            "transactions-1-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-1-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-1-total": 0,
            "transactions-1-currency": self.transaction.currency,
            "transactions-1-shop": f"{self.shop.id}",
            "transactions-1-date": self.transaction.date.strftime("%Y-%m-%d"),
        }

        with self.subTest("If form is invalid, should not show confirmation page"):
            data = {
                **form_data,
                "Transaction_confirm_change": True,
                "_save": "Save",
            }
            response = self.client.post(
                reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
            )

            # Invalid form should not redirect
            self.assertEqual(response.status_code, 200)
            # And should not show confirmation page, instead shows the change form with errors
            expected_templates = [
                "admin/market/consumer/change_form.html",
                "admin/market/change_form.html",
                "admin/change_form.html",
            ]
            self.assertEqual(response.template_name, expected_templates)
            formset_errors = response.context_data.get("inline_admin_formsets")[0].formset.errors
            self.assertIsNotNone(formset_errors)
            self.assertEqual(
                formset_errors,
                # First form without errors, second form with error on consumer field
                [{}, {"consumer": ["The inline value did not match the parent instance."]}],
            )

            # This transaction should not have changed since form invalid
            self.transaction.refresh_from_db()
            self.assertNotEqual(self.transaction.total, 999.00)

            # Nor should a new transaction have been added
            self.assertEqual(Transaction.objects.count(), 1)

        with self.subTest(
            "If errors on change form are fixed, confirmation page should show up on next submission"
        ):
            form_data["transactions-1-consumer"] = self.consumer.id
            data = {
                **form_data,
                "Transaction_confirm_change": True,  # Not stripped yet
                "_save": "Save",
            }
            response = self.client.post(
                reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
            )
            # Ensure not redirected (confirmation page does not redirect)
            self.assertEqual(response.status_code, 200)
            expected_templates = [
                "admin/market/consumer/change_confirmation.html",
                "admin/market/change_confirmation.html",
                "admin/change_confirmation.html",
            ]
            self.assertEqual(response.template_name, expected_templates)
            # Should not have made any changes yet, since confirmation page is shown
            self.transaction.refresh_from_db()
            self.assertNotEqual(self.transaction.total, 999.00)
            self.assertEqual(Transaction.objects.count(), 1)

        with self.subTest("If confirmation page is submitted, changes should be made"):
            data = {
                **form_data,
                # Confirmation page submissions does not include confirmation options
                "_save": "Save",
            }
            response = self.client.post(
                reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
            )
            # Ensure redirected to changelist after confirmation page submission
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/admin/market/consumer/")
            # Should have updated original transaction and added new transaction on confirmation page
            self.transaction.refresh_from_db()
            self.assertEqual(self.transaction.total, 999.00)
            self.assertEqual(Transaction.objects.count(), 2)

    def test_inline_confirmation_fields_set_with_confirm_change(self):
        self.setAdminAttributes(
            TransactionInline, confirm_change=True, confirmation_fields=["currency"]
        )
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "Transaction_confirm_change": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        # Redirects to changelist, since total is not a confirmation field, it should not trigger confirmation page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/consumer/")
        # Transaction has been updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.total, 999.00)

    def test_no_change_permissions(self):
        user = User.objects.create_user(username="user", is_staff=True)
        self.client.force_login(user)

        self.setAdminAttributes(
            TransactionInline, confirm_change=True, confirmation_fields=["currency"]
        )
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "Transaction_confirm_change": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(isinstance(response, HttpResponseForbidden))

        self.transaction.refresh_from_db()
        # Transaction should not have been updated since user has no change permissions
        self.assertNotEqual(self.transaction.total, 999.00)

    def test_no_add_permissions(self):
        user = User.objects.create_user(username="user", is_staff=True)
        self.client.force_login(user)

        self.setAdminAttributes(TransactionInline, confirm_add=False)
        data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "0",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": "",
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": str(self.transaction.total),
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(isinstance(response, HttpResponseForbidden))

        # Should not have been added
        self.assertEqual(Transaction.objects.count(), 0)

    def test_no_delete_permissions(self):
        user = User.objects.create_user(username="user", is_staff=True)
        self.client.force_login(user)

        self.setAdminAttributes(TransactionInline, confirm_delete=False)
        self.transaction.save()
        form_data = {
            "name": self.consumer.name,
            "email": self.consumer.email,
            "transactions-TOTAL_FORMS": "1",
            "transactions-INITIAL_FORMS": "1",
            "transactions-MIN_NUM_FORMS": "0",
            "transactions-MAX_NUM_FORMS": "1000",
            "transactions-0-id": self.transaction.id,
            "transactions-0-consumer": self.consumer.id,
            "transactions-0-timestamp_0": self.transaction.timestamp.strftime("%Y-%m-%d"),
            "transactions-0-timestamp_1": self.transaction.timestamp.strftime("%H:%M:%S"),
            "transactions-0-total": 999.00,  # Change total to trigger confirmation
            "transactions-0-currency": self.transaction.currency,
            "transactions-0-shop": f"{self.shop.id}",
            "transactions-0-date": self.transaction.date.strftime("%Y-%m-%d"),
        }
        data = {
            **form_data,
            "transactions-0-DELETE": True,
            "_save": "Save",
        }
        response = self.client.post(
            reverse("admin:market_consumer_change", args=[self.consumer.id]), data=data
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(isinstance(response, HttpResponseForbidden))
        # Transaction not deleted
        self.assertEqual(Transaction.objects.count(), 1)
