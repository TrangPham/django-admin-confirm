"""
Tests ModelAdmin with fieldsets custom configured through one of the possible methods
Ensures that AdminConfirmMixin works correctly when implimenting class alters default fieldsets

Test Matrix
method: `.fieldsets =`, `def get_fieldsets()`
action: change, add
fieldset: simple, with readonly fields, with custom fields
"""
import pytest
from importlib import reload
from tests.market.admin import item_admin

from django.contrib.auth.models import User
from django.contrib.admin import AdminSite
from django.test.client import RequestFactory


from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from admin_confirm.constants import CACHE_KEYS, CONFIRM_CHANGE, CONFIRMATION_RECEIVED

from tests.market.models import Item
from tests.factories import ItemFactory


def fs_simple(admin):
    return (
        (None, {"fields": ("name", "price", "image")}),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": ("currency", "file"),
            },
        ),
    )


def fs_w_readonly(admin):
    admin.readonly_fields = ["description", "image"]
    return fs_simple(admin)


def fs_w_custom(admin):
    admin.one = lambda self, obj: "ReadOnly"
    admin.two = lambda self, obj: "ReadOnly"
    admin.three = lambda self, obj: "ReadOnly"
    admin.readonly_fields = ["one", "two", "three"]
    return (
        (None, {"fields": ("name", "price", "image", "one")}),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": ("currency", "two", "file"),
            },
        ),
        ("More Info", {"fields": ("three", "description")}),
    )


def set_fieldsets(admin, fieldset):
    admin.fieldsets = fieldset


def override_get_fieldsets(admin, fieldset):
    admin.get_fieldsets = lambda self, request, obj=None: fieldset


methods = [set_fieldsets, override_get_fieldsets]
actions = ["_confirm_add", "_confirm_change"]
fieldsets = [fs_simple, fs_w_readonly, fs_w_custom]

param_matrix = []
for method in methods:
    for fieldset in fieldsets:
        for action in actions:
            param_matrix.append((method, fieldset, action))


@pytest.mark.django_db()
@pytest.mark.parametrize("method,get_fieldset,action", param_matrix)
def test_fieldsets(client, method, get_fieldset, action):
    reload(item_admin)

    admin = item_admin.ItemAdmin
    fs = get_fieldset(admin)
    # set fieldsets via one of the methods
    method(admin, fs)

    admin_instance = admin(admin_site=AdminSite(), model=Item)
    request = RequestFactory().request
    assert admin_instance.get_fieldsets(request) == fs

    user = User.objects.create_superuser(
        username="super", email="super@email.org", password="pass"
    )
    client.force_login(user)

    url = "/admin/market/item/add/"
    image_path = "screenshot.png"
    f2 = SimpleUploadedFile(
        name="new_file.jpg",
        content=open(image_path, "rb").read(),
        content_type="image/jpeg",
    )
    i2 = SimpleUploadedFile(
        name="new_image.jpg",
        content=open(image_path, "rb").read(),
        content_type="image/jpeg",
    )
    data = {
        "name": "new name",
        "price": 2,
        "currency": "USD",
        "image": i2,
        "file": f2,
        action: True,
        "_save": True,
    }
    for f in admin.readonly_fields:
        if f in data.keys():
            del data[f]
    if action == CONFIRM_CHANGE:
        url = "/admin/market/item/1/change/"
        f = SimpleUploadedFile(
            name="old_file.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        i = SimpleUploadedFile(
            name="old_image.jpg",
            content=open(image_path, "rb").read(),
            content_type="image/jpeg",
        )
        item = ItemFactory(name="old name", price=1, currency="CAD", file=f, image=i)
        data["id"] = item.id

    cache_item = Item()
    for f in ["name", "price", "currency", "image", "file"]:
        if f not in admin.readonly_fields:
            setattr(cache_item, f, data[f])

    cache.set(CACHE_KEYS["object"], cache_item)
    cache.set(CACHE_KEYS["post"], data)

    # Click "Yes, I'm Sure"
    del data[action]
    data[CONFIRMATION_RECEIVED] = True
    response = client.post(url, data=data)

    # Should have redirected to changelist
    # assert response.status_code == 302
    assert response.url == "/admin/market/item/"

    # Should have saved item
    assert Item.objects.count() == 1
    saved_item = Item.objects.all().first()
    for f in ["name", "price", "currency"]:
        if f not in admin.readonly_fields:
            assert getattr(saved_item, f) == data[f]
    if "file" not in admin.readonly_fields:
        assert "new_file" in saved_item.file.name
    if "image" not in admin.readonly_fields:
        assert "new_image" in saved_item.image.name

    reload(item_admin)
