from django.test import SimpleTestCase

from admin_confirm import AdminConfirmMixin, confirm_action
from admin_confirm.exceptions import FormNotBoundException
from admin_confirm.utils import snake_to_title_case


class TestUtilsAndExports(SimpleTestCase):
    def test_snake_to_title_case(self):
        self.assertEqual(snake_to_title_case("save_as_new"), "Save As New")

    def test_package_exports(self):
        self.assertTrue(callable(confirm_action))
        self.assertIsNotNone(AdminConfirmMixin)

    def test_form_not_bound_exception(self):
        with self.assertRaises(FormNotBoundException):
            raise FormNotBoundException("not bound")
