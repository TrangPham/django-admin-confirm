from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User


class ConfirmAdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="super", email="super@email.org", password="pass"
        )

    def setUp(self):
        self.client.force_login(self.superuser)
        self.factory = RequestFactory()

    def _assertManyToManyFormHtml(self, rendered_content, options, selected_ids):
        # Form data should be embedded and hidden on confirmation page
        # Should have the correct ManyToMany options selected
        for option in options:
            self.assertIn(
                f'<option value="{option.id}"{" selected" if option.id in selected_ids else ""}>{str(option)}</option>',
                rendered_content,
            )
        # ManyToManyField should be embedded
        self.assertIn("related-widget-wrapper", rendered_content)

    def _assertSubmitHtml(self, rendered_content, save_action="_save"):
        # Submit should conserve the save action
        self.assertIn(
            f'<input type="submit" value="Yes, I’m sure" name="{save_action}">',
            rendered_content,
        )
        # There should not be _confirm_add or _confirm_change sent in the form on confirmaiton page
        self.assertNotIn("_confirm_add", rendered_content)
        self.assertNotIn("_confirm_change", rendered_content)
        # Should have _confirmation_received as a hidden field
        self.assertIn(
            '<input type="hidden" name="_confirmation_received" value="True">',
            rendered_content,
        )

    def _assertSimpleFieldFormHtml(self, rendered_content, fields):
        for k, v in fields.items():
            self.assertIn(f'name="{k}"', rendered_content)
            self.assertIn(f'value="{v}"', rendered_content)
