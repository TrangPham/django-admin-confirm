from .base import *

INSTALLED_APPS = INSTALLED_APPS + ['tests.market']
WSGI_APPLICATION = "tests.test_project.wsgi.application"
ROOT_URLCONF = "tests.test_project.urls"
