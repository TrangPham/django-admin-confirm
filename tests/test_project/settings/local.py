from .base import *

INSTALLED_APPS = INSTALLED_APPS + ["market"]
WSGI_APPLICATION = "test_project.wsgi.application"
ROOT_URLCONF = "test_project.urls"

USE_S3 = "True"
