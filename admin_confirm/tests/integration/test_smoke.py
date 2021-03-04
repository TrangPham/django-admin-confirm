from admin_confirm.tests.helpers import AdminConfirmIntegrationTestCase


class SmokeTest(AdminConfirmIntegrationTestCase):
    def test_load_admin(self):
        self.selenium.get(self.live_server_url + "/admin/")
        self.assertIn("Django", self.selenium.title)
        self.assertIn("Market", self.selenium.page_source)
