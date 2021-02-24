from django.contrib.admin import ModelAdmin
from admin_confirm.admin import AdminConfirmMixin


class InventoryAdmin(AdminConfirmMixin, ModelAdmin):
    list_display = ("shop", "item", "quantity")
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]
