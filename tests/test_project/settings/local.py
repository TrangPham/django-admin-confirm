from .base import *

INSTALLED_APPS = INSTALLED_APPS + ["market"]
WSGI_APPLICATION = "test_project.wsgi.application"
ROOT_URLCONF = "test_project.urls"

if USE_S3:
    STATICFILES_STORAGE = "storage_backends.StaticStorage"
    DEFAULT_FILE_STORAGE = "storage_backends.PublicMediaStorage"
