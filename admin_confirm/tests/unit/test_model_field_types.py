from django.urls import reverse
from django.utils import timezone

from admin_confirm.tests.helpers import AdminConfirmTestCase
from tests.market.models import Transaction
from tests.factories import ShopFactory, TransactionFactory


class TestModelFieldTypes(AdminConfirmTestCase):
    def test_confirm_add_of_datetime_and_field(self):
        shop = ShopFactory()
        expected_date = timezone.now().date()
        expected_timestamp = timezone.now()
        data = {
            "date": str(expected_date),
            "timestamp_0": str(expected_timestamp.date()),
            "timestamp_1": str(expected_timestamp.time()),
            "currency": "USD",
            "shop": shop.id,
            "_confirm_add": True,
            "_save": True,
        }
        response = self.client.post(reverse("admin:market_transaction_add"), data)

        # Should not have been added yet
        self.assertEqual(Transaction.objects.count(), 0)

        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/transaction/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(rendered_content=response.rendered_content)

        # Confirmation page would not have the _confirm_add sent on submit
        del data["_confirm_add"]
        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        response = self.client.post(reverse("admin:market_transaction_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/market/transaction/")
        self.assertEqual(Transaction.objects.count(), 1)

        # Ensure that the date and timestamp saved correctly
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.date, expected_date)
        self.assertEqual(transaction.timestamp, expected_timestamp)

    def test_confirm_change_of_datetime_and_date_field(self):
        transaction = TransactionFactory()
        original_date = transaction.date
        original_timestamp = transaction.timestamp
        data = {
            "id": transaction.id,
            "date": "2021-01-01",
            "timestamp_0": "2021-01-01",
            "timestamp_1": "12:30:00",
            "currency": "USD",
            "shop": transaction.shop.id,
            "_confirm_change": True,
            "csrfmiddlewaretoken": "fake token",
            "_continue": True,
        }
        response = self.client.post(
            f"/admin/market/transaction/{transaction.id}/change/", data
        )
        # Ensure not redirected (confirmation page does not redirect)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            "admin/market/transaction/change_confirmation.html",
            "admin/market/change_confirmation.html",
            "admin/change_confirmation.html",
        ]
        self.assertEqual(response.template_name, expected_templates)

        self._assertSubmitHtml(
            rendered_content=response.rendered_content, save_action="_continue"
        )

        # Hasn't changed item yet
        transaction.refresh_from_db()
        self.assertEqual(transaction.date, original_date)
        self.assertEqual(transaction.timestamp, original_timestamp)

        # Selecting to "Yes, I'm sure" on the confirmation page
        # Would post to the same endpoint
        del data["_confirm_change"]
        response = self.client.post(
            f"/admin/market/transaction/{transaction.id}/change/", data
        )
        # will show the change page for this transaction
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/admin/market/transaction/{transaction.id}/change/"
        )
        # Should not be the confirmation page, we already confirmed change
        self.assertNotEqual(response.templates, expected_templates)
        self.assertEqual(Transaction.objects.count(), 1)

        transaction.refresh_from_db()
        self.assertEqual(str(transaction.date), "2021-01-01")
        self.assertEqual(str(transaction.timestamp.date()), "2021-01-01")
        self.assertEqual(str(transaction.timestamp.time()), "12:30:00")
