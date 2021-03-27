from admin_confirm.admin import AdminConfirmMixin


from django.contrib.admin import ModelAdmin


class ItemSaleAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
