from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission, User
from django.urls import reverse


from tests.market.admin import ShopAdmin
from tests.market.models import Shop


class TestConfirmActions(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="super", email="super@email.org", password="pass"
        )

    def setUp(self):
        self.client.force_login(self.superuser)
        self.factory = RequestFactory()

    def test_get_changelist_should_not_be_affected(self):
        response = self.client.get(reverse("admin:market_shop_changelist"))
        self.assertIsNotNone(response)
        self.assertNotIn("Confirm Action", response.rendered_content)

    def test_action_without_confirmation(self):
        post_params = {
            "action": ["show_message_no_confirmation"],
            "select_across": ["0"],
            "index": ["0"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmaiton page
        self.assertNotIn("action_confirmation", response.template_name)

        # The action was to show user a message
        self.assertIn("You selected without confirmation", response.rendered_content)

    def test_action_with_confirmation_should_show_confirmation_page(self):
        post_params = {
            "action": ["show_message"],
            "select_across": ["0"],
            "index": ["0"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should use confirmaiton page
        self.assertEqual(
            response.template_name,
            [
                "admin/market/shop/action_confirmation.html",
                "admin/market/action_confirmation.html",
                "admin/action_confirmation.html",
            ],
        )

        # The action was to show user a message, and should not happen yet
        self.assertNotIn("You selected", response.rendered_content)

    def test_no_permissions_in_database_for_action_with_confirmation(self):
        """
        Django would not show the action in changelist action selector
        If the user doesn't have permissions, but this doesn't prevent
        user from calling post with the params to perform the action.

        If the permissions are denied because of Permission in the database,
        Django would redirect to the changelist.
        """
        # Create a user without permissions for action
        user = User.objects.create_user(
            username="user",
            email="user@email.org",
            password="pass",
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        # Give user permissions to ShopAdmin change, add, view but not delete
        for permission in Permission.objects.filter(
            codename__in=["change_shop", "view_shop", "add_shop"]
        ):
            user.user_permissions.add(permission)

        self.client.force_login(user)

        post_params = {
            "action": ["show_message"],
            "select_across": ["0"],
            "index": ["0"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmaiton page
        self.assertEqual(
            response.template_name,
            [
                "admin/market/shop/change_list.html",
                "admin/market/change_list.html",
                "admin/change_list.html",
            ],
        )

        # The action was to show user a message, and should not happen
        self.assertNotIn("You selected", response.rendered_content)

        # Django won't show the action as an option to you
        self.assertIn("No action selected", response.rendered_content)

    def test_no_permissions_in_code_non_superuser_for_action_with_confirmation(self):
        """
        Django would not show the action in changelist action selector
        If the user doesn't have permissions, but this doesn't prevent
        user from calling post with the params to perform the action.

        If the permissions are denied because of Permission in the database,
        Django would redirect to the changelist.

        It should also respect the has_xxx_permission methods
        """
        # Create a user without permissions for action
        user = User.objects.create_user(
            username="user",
            email="user@email.org",
            password="pass",
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        # Give user permissions to ShopAdmin change, add, view and delete
        for permission in Permission.objects.filter(
            codename__in=["change_shop", "view_shop", "add_shop", "delete_shop"]
        ):
            user.user_permissions.add(permission)

        self.client.force_login(user)

        # ShopAdmin has defined:
        #   def has_delete_permission(self, request, obj=None):
        #       return request.user.is_superuser

        post_params = {
            "action": ["show_message"],
            "select_across": ["0"],
            "index": ["0"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmaiton page
        self.assertEqual(
            response.template_name,
            [
                "admin/market/shop/change_list.html",
                "admin/market/change_list.html",
                "admin/change_list.html",
            ],
        )

        # The action was to show user a message, and should not happen yet
        self.assertNotIn("You selected", response.rendered_content)

        # Django won't show the action as an option to you
        self.assertIn("No action selected", response.rendered_content)

    def test_no_permissions_in_code_superuser_for_action_with_confirmation(self):
        """
        Django would not show the action in changelist action selector
        If the user doesn't have permissions, but this doesn't prevent
        user from calling post with the params to perform the action.

        When permissions are denied from a change in code
        (ie has_xxx_permission in ModelAdmin), Django should still
        redirect to changelist. This should be true even if the user is
        a superuser.
        """
        # ShopAdmin has defined:
        #   def has_delete_permission(self, request, obj=None):
        #       return request.user.is_superuser

        ShopAdmin.has_delete_permission = lambda self, request, obj=None: False
        post_params = {
            "action": ["show_message"],
            "select_across": ["0"],
            "index": ["0"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmaiton page
        self.assertEqual(
            response.template_name,
            [
                "admin/market/shop/change_list.html",
                "admin/market/change_list.html",
                "admin/change_list.html",
            ],
        )

        # The action was to show user a message, and should not happen yet
        self.assertNotIn("You selected", response.rendered_content)

        # Django won't show the action as an option to you
        self.assertIn("No action selected", response.rendered_content)

        # Remove our modification for ShopAdmin
        ShopAdmin.has_delete_permission = (
            lambda self, request, obj=None: request.user.is_superuser
        )

    def test_confirm_action_submit_button_should_perform_action(self):
        """
        The submit button should have param "_confirm_action"

        Simulate calling the post request that the button would
        """
        post_params = {
            "_confirm_action": ["Yes, I'm sure"],
            "action": ["show_message"],
            "_selected_action": ["3", "2", "1"],
        }
        response = self.client.post(
            reverse("admin:market_shop_changelist"),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmaiton page, since we clicked Yes, I'm sure
        self.assertEqual(
            response.template_name,
            [
                "admin/market/shop/change_list.html",
                "admin/market/change_list.html",
                "admin/change_list.html",
            ],
        )

        # The action was to show user a message, and should happen
        self.assertIn("You selected", response.rendered_content)

    def test_should_use_action_confirmation_template_if_set(self):
        expected_template = "market/admin/my_custom_template.html"
        ShopAdmin.action_confirmation_template = expected_template
        admin = ShopAdmin(Shop, AdminSite())
        actual_template = admin.render_action_confirmation(
            self.factory.request(), context={}
        ).template_name
        self.assertEqual(expected_template, actual_template)
        # Clear our setting to not affect other tests
        ShopAdmin.action_confirmation_template = None
