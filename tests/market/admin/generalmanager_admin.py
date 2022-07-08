from django.contrib.admin import ModelAdmin
from admin_confirm.admin import AdminConfirmMixin


class GeneralManagerAdmin(AdminConfirmMixin, ModelAdmin):
    save_as = True
    search_fields = ["name"]
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["name", "headshot"]
