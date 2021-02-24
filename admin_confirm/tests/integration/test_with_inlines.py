# """
# Tests confirmation of add/change
# on ModelAdmin that includes inlines

# Does not test confirmation of inline changes
# """
# from importlib import reload
# from tests.factories import ShopFactory
# from tests.market.models import GeneralManager, Shop, ShoppingMall, Town

# from admin_confirm.tests.helpers import AdminConfirmTestCase
# from tests.market.admin import shoppingmall_admin


# class ConfirmWithInlinesTests(AdminConfirmTestCase):
#     def setUp(self):
#         self.admin = shoppingmall_admin.ShoppingMallAdmin
#         self.admin.inlines = [shoppingmall_admin.ShopInline]
#         super().setUp()

#     def tearDown(self):
#         reload(shoppingmall_admin)
#         super().tearDown()

#     def test_should_have_hidden_formsets(self):
#         # Not having these would cause a `ManagementForm tampered with` issue
#         gm = GeneralManager.objects.create(name="gm")
#         shops = [ShopFactory(name=i) for i in range(3)]
#         town = Town.objects.create(name="town")
#         mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)

#         # new values
#         gm2 = GeneralManager.objects.create(name="gm2")
#         shops2 = [ShopFactory(name=i) for i in range(3)]
#         town2 = Town.objects.create(name="town2")

#         response = self.client.get(f"/admin/market/shoppingmall/{mall.id}/change/")
#         print(response.rendered_content)
#         # print(response)
#         # print(response.context.keys())
#         # print(response.wsgi_request.read())
#         # print(response.wsgi_request.body)
#         # print(response.context_data)
#         # print(response.context["csrf_token"])
#         # print(type(response.context[0]))
#         # for k in response.context:
#         #     print(k)
#         # print(response.context)
#         management_form = response.context["form"].management_form
#         print(management_form)
#         assert False
#         data = {
#             "id": ["1"],
#             "name": ["11"],
#             "shops": ["1", "2"],
#             "general_manager": ["2"],
#             "town": [""],
#             "ShoppingMall_shops-TOTAL_FORMS": ["5"],
#             "ShoppingMall_shops-INITIAL_FORMS": ["2"],
#             "ShoppingMall_shops-MIN_NUM_FORMS": ["0"],
#             "ShoppingMall_shops-MAX_NUM_FORMS": ["1000"],
#             "ShoppingMall_shops-0-shop": ["0"],
#             "ShoppingMall_shops-0-id": [1],
#             "ShoppingMall_shops-0-shoppingmall": ["1"],
#             "ShoppingMall_shops-1-shop": ["1"],
#             "ShoppingMall_shops-1-id": [2],
#             "ShoppingMall_shops-1-shoppingmall": ["1"],
#             "ShoppingMall_shops-2-shop": [""],
#             "ShoppingMall_shops-2-id": [""],
#             "ShoppingMall_shops-2-shoppingmall": ["1"],
#             "ShoppingMall_shops-3-shop": [""],
#             "ShoppingMall_shops-3-id": [""],
#             "ShoppingMall_shops-3-shoppingmall": ["1"],
#             "ShoppingMall_shops-4-shop": [""],
#             "ShoppingMall_shops-4-id": [""],
#             "ShoppingMall_shops-4-shoppingmall": ["1"],
#             "ShoppingMall_shops-__prefix__-shop": [""],
#             "ShoppingMall_shops-__prefix__-id": [""],
#             "ShoppingMall_shops-__prefix__-shoppingmall": ["1"],
#             "_confirm_change": ["True"],
#             "_confirm_add": ["True"],
#             "_save": ["Save"],
#         }
#         # data = {
#         #     "id": mall.id,
#         #     "name": "name",
#         #     "general_manager": gm2.id,
#         #     "shops": [1],
#         #     "town": town2.id,
#         #     "_confirm_change": True,
#         #     "_continue": True,
#         # }
#         response = self.client.post(
#             f"/admin/market/shoppingmall/{mall.id}/change/", data=data
#         )
#         # print(response.wsgi_request.POST)
#         # print(response.content)
#         # print(response.context)
#         # print(dir(response))
#         # print(response.json())

#         # Should be shown confirmation page
#         self._assertSubmitHtml(
#             rendered_content=response.rendered_content, save_action="_continue"
#         )

#         form_fields = data.copy()
#         del form_fields["_confirm_change"]
#         del form_fields["_save"]
#         # Should have hidden form fields
#         self._assertSimpleFieldFormHtml(
#             rendered_content=response.rendered_content,
#         )

#         # Should have hidden formsets for inlines
#         self._assertFormsetsFormHtml(
#             rendered_content=response.rendered_content, inlines=self.admin.inlines
#         )


# # TODO

# # import pytest
# # from importlib import reload
# # from tests.market.admin import item_admin

# # from django.contrib.auth.models import User
# # from django.contrib.admin import AdminSite
# # from django.test.client import RequestFactory


# # from django.core.files.uploadedfile import SimpleUploadedFile
# # from django.core.cache import cache

# # from admin_confirm.constants import CACHE_KEYS, CONFIRM_CHANGE

# # from tests.market.models import Item
# # from tests.factories import ItemFactory

# # # Test Matrix

# # # action: change, add
# # # fieldset:
# # #   simple inline,
# # #   inline with readonly fields,
# # #   inline with custom fields,

# # # method:
# # #  .inlines
# # #  .get_inline_instances()
# # #  .get_inlines() (New in Django 3.0)
# # #  .get_formsets_with_inlines()


# # def fs_simple(admin):
# #     return (
# #         (None, {"fields": ("name", "price", "image")}),
# #         (
# #             "Advanced options",
# #             {
# #                 "classes": ("collapse",),
# #                 "fields": ("currency", "file"),
# #             },
# #         ),
# #     )


# # def fs_w_readonly(admin):
# #     admin.readonly_fields = ["description", "image"]
# #     return fs_simple(admin)


# # def fs_w_custom(admin):
# #     admin.readonly_fields = ["one", "two", "three"]
# #     return (
# #         (None, {"fields": ("name", "price", "image", "one")}),
# #         (
# #             "Advanced options",
# #             {
# #                 "classes": ("collapse",),
# #                 "fields": ("currency", "two", "file"),
# #             },
# #         ),
# #         ("More Info", {"fields": ("three", "description")}),
# #     )


# # def set_fieldsets(admin, fieldset):
# #     admin.fieldsets = fieldset


# # def override_get_fieldsets(admin, fieldset):
# #     admin.get_fieldsets = lambda self, request, obj=None: fieldset


# # methods = [set_fieldsets, override_get_fieldsets]
# # actions = ["_confirm_add", "_confirm_change"]
# # fieldsets = [fs_simple, fs_w_readonly, fs_w_custom]

# # param_matrix = []
# # for method in methods:
# #     for fieldset in fieldsets:
# #         for action in actions:
# #             param_matrix.append((method, fieldset, action))


# # @pytest.mark.django_db()
# # @pytest.mark.parametrize("method,get_fieldset,action", param_matrix)
# # def test_fieldsets(client, method, get_fieldset, action):
# #     reload(item_admin)

# #     admin = item_admin.ItemAdmin
# #     fs = get_fieldset(admin)
# #     # set fieldsets via one of the methods
# #     method(admin, fs)

# #     admin_instance = admin(admin_site=AdminSite(), model=Item)
# #     request = RequestFactory().request
# #     assert admin_instance.get_fieldsets(request) == fs

# #     user = User.objects.create_superuser(
# #         username="super", email="super@email.org", password="pass"
# #     )
# #     client.force_login(user)

# #     url = "/admin/market/item/add/"
# #     image_path = "screenshot.png"
# #     f2 = SimpleUploadedFile(
# #         name="new_file.jpg",
# #         content=open(image_path, "rb").read(),
# #         content_type="image/jpeg",
# #     )
# #     i2 = SimpleUploadedFile(
# #         name="new_image.jpg",
# #         content=open(image_path, "rb").read(),
# #         content_type="image/jpeg",
# #     )
# #     data = {
# #         "name": "new name",
# #         "price": 2,
# #         "currency": "USD",
# #         "image": i2,
# #         "file": f2,
# #         action: True,
# #         "_save": True,
# #     }
# #     for f in admin.readonly_fields:
# #         if f in data.keys():
# #             del data[f]
# #     if action == CONFIRM_CHANGE:
# #         url = "/admin/market/item/1/change/"
# #         f = SimpleUploadedFile(
# #             name="old_file.jpg",
# #             content=open(image_path, "rb").read(),
# #             content_type="image/jpeg",
# #         )
# #         i = SimpleUploadedFile(
# #             name="old_image.jpg",
# #             content=open(image_path, "rb").read(),
# #             content_type="image/jpeg",
# #         )
# #         item = ItemFactory(name="old name", price=1, currency="CAD", file=f, image=i)
# #         data["id"] = item.id

# #     cache_item = Item()
# #     for f in ["name", "price", "currency", "image", "file"]:
# #         if f not in admin.readonly_fields:
# #             setattr(cache_item, f, data[f])

# #     cache.set(CACHE_KEYS["object"], cache_item)
# #     cache.set(CACHE_KEYS["post"], data)

# #     # Click "Yes, I'm Sure"
# #     del data[action]
# #     data["_confirmation_received"] = True
# #     response = client.post(url, data=data)

# #     # Should have redirected to changelist
# #     # assert response.status_code == 302
# #     assert response.url == "/admin/market/item/"

# #     # Should have saved item
# #     assert Item.objects.count() == 1
# #     saved_item = Item.objects.all().first()
# #     for f in ["name", "price", "currency"]:
# #         if f not in admin.readonly_fields:
# #             assert getattr(saved_item, f) == data[f]
# #     if "file" not in admin.readonly_fields:
# #         assert "new_file" in saved_item.file.name
# #     if "image" not in admin.readonly_fields:
# #         assert "new_image" in saved_item.image.name

# #     reload(item_admin)
