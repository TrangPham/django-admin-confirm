from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe
from admin_confirm.admin import AdminConfirmMixin


class ItemAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["price"]

    list_display = ("name", "price", "currency")
    readonly_fields = ["image_preview"]

    save_as = True
    save_as_continue = False

    def image_preview(self, obj):
        if obj.image:
            return mark_safe('<img src="{obj.image.url}" />')

    def one(self, obj):
        return "Read Only"

    def two(self, obj):
        return "Read Only"

    def three(self, obj):
        return "Read Only"
