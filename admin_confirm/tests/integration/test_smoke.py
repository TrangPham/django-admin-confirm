import socket
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class FunctionalTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


    def test_user_registration(self):
        self.selenium.get(self.live_server_url+'/admin/')
        self.assertIn('Django', self.selenium.title)
