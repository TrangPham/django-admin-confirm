from admin_confirm.constants import DEBUG
from django.urls import reverse


def snake_to_title_case(string: str) -> str:
    return " ".join(string.split("_")).title()


def get_admin_change_url(obj):
    return reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=(obj.pk,),
    )


def log(message: str):
    if DEBUG:
        print(message)


def inspect(obj: object):
    if DEBUG:
        print(f"{str(object): type(object) - dir(object)}")
