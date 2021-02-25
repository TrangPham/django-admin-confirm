from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class FunctionalTestCase(LiveServerTestCase):
    host = 'web'
    def setUp(self):
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX
        )

    def test_user_registration(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Django', self.browser.title)

    def tearDown(self):
        self.browser.close()
