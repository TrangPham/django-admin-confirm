"""
Ensure that files are saved during confirmation
Without file changes, Django is relied on

With file changes, we cache the object, save it with
the files if new, or add files to existing obj and save

Then send the rest of the changes to Django to handle

This is arguably the most we fiddle with the Django request
Thus we should test it extensively
"""
from admin_confirm.tests.helpers import AdminConfirmTestCase
from admin_confirm.constants import CONFIRM_ADD, CONFIRM_CHANGE, CONFIRMATION_RECEIVED


class FileCacheUnitTests(AdminConfirmTestCase):
    def test_save_as_continue_true_should_not_redirect_to_changelist(self):
        # Check url
        # Check url and message to user
        pass

    def test_save_as_continue_false_should_redirect_to_changelist(self):
        # Check url
        # Check url and message to user
        pass

    def test_without_any_file_changes(self):
        pass

    def test_upload_image_and_file(self):
        pass

    def test_clear_file(self):
        pass

    def test_add_with_upload_file(self):
        pass

    def test_should_not_contain_admin_confirm_tags_in_post(self):
        for tag in [CONFIRM_ADD, CONFIRM_CHANGE, CONFIRMATION_RECEIVED]:
            pass
        pass
