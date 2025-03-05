from admin_confirm.admin import AdminConfirmMixin


from django.contrib.admin import ModelAdmin
from django.contrib import admin


class TransactionAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True

    readonly_fields = ["my_custom_field"]

    @admin.display(description="Custom Field")
    def my_custom_field(self, obj):
        return "Static Custom Field Value"
