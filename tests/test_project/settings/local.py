from .base import *

INSTALLED_APPS = INSTALLED_APPS + ["market"]
WSGI_APPLICATION = "test_project.wsgi.application"
ROOT_URLCONF = "test_project.urls"

if USE_S3:
    if DJANGO_VERSION >= "4.2":
        STORAGES = {
            "default": {
                "BACKEND": "storage_backends.PublicMediaStorage",
                "OPTIONS": {
                    "location": "staticfiles",
                },
            },
            "staticfiles": {
                "BACKEND": "storage_backends.StaticStorage",
                "OPTIONS": {
                    "location": "mediafiles",
                },
            },
        }
    else:
        STATICFILES_STORAGE = "storage_backends.StaticStorage"
        DEFAULT_FILE_STORAGE = "storage_backends.PublicMediaStorage"
