from django.conf import settings

SAVE = "_save"
SAVE_AS_NEW = "_saveasnew"
ADD_ANOTHER = "_addanother"
SAVE_AND_CONTINUE = "_continue"
SAVE_ACTIONS = [SAVE, SAVE_AS_NEW, ADD_ANOTHER, SAVE_AND_CONTINUE]

CONFIRM_ADD = "_confirm_add"
CONFIRM_CHANGE = "_confirm_change"
CONFIRMATION_RECEIVED = "_confirmation_received"

CACHE_TIMEOUT = getattr(settings, "ADMIN_CONFIRM_CACHE_TIMEOUT", 1000)
CACHE_KEYS = {
    "object": "admin_confirm__confirmation_object",
    "post": "admin_confirm__confirmation_request_post",
}
CACHE_KEY_PREFIX = getattr(
    settings, "ADMIN_CONFIRM_CACHE_KEY_PREFIX", "admin_confirm__file_cache"
)


DEBUG = getattr(settings, "ADMIN_CONFIRM_DEBUG", False)
