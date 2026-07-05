from django.test import SimpleTestCase

from admin_confirm.templatetags.formatting import (
    format_change_data_field_value,
    verbose_name,
)
from tests.market.models import Item


class _BrokenIterable:
    def __iter__(self):
        raise RuntimeError("broken")


class TestFormattingTemplateTags(SimpleTestCase):
    def test_format_change_data_field_value_should_fallback_on_iter_error(self):
        broken = _BrokenIterable()

        self.assertIs(format_change_data_field_value(broken), broken)

    def test_verbose_name_should_capitalize_field_name(self):
        self.assertEqual(verbose_name(Item._meta, "name"), "Name")
