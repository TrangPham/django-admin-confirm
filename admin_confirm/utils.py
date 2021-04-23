from django.urls import reverse
from admin_confirm.constants import CACHE_KEY_PREFIX, DEBUG


def snake_to_title_case(string: str) -> str:
    return " ".join(string.split("_")).title()


def get_admin_change_url(obj: object) -> str:
    return reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=(obj.pk,),
    )


def format_cache_key(model: str, field: str) -> str:
    return f"{CACHE_KEY_PREFIX}__{model}__{field}"


def log(message: str):  # pragma: no cover
    if DEBUG:
        print(message)


def inspect(obj: object):  # pragma: no cover
    if DEBUG:
        print(f"{str(obj): type(obj) - dir(obj)}")
