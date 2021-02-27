from django.contrib.admin import ModelAdmin
from admin_confirm.admin import AdminConfirmMixin, confirm_action


class ShopAdmin(AdminConfirmMixin, ModelAdmin):
    confirmation_fields = ["name"]
    actions = ["show_message", "show_message_no_confirmation"]

    @confirm_action
    def show_message(modeladmin, request, queryset):
        shops = ", ".join(shop.name for shop in queryset)
        modeladmin.message_user(request, f"You selected with confirmation: {shops}")

    show_message.allowed_permissions = ("delete",)

    def show_message_no_confirmation(modeladmin, request, queryset):
        shops = ", ".join(shop.name for shop in queryset)
        modeladmin.message_user(request, f"You selected without confirmation: {shops}")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
