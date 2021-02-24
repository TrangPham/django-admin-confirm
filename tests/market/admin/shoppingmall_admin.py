from django.contrib.admin import ModelAdmin
from admin_confirm.admin import AdminConfirmMixin


class ShoppingMallAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
    confirmation_fields = ["name"]
