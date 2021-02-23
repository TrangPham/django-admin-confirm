from django.contrib import admin
from django.utils.safestring import mark_safe


from admin_confirm.admin import AdminConfirmMixin, confirm_action

from .models import Item, Inventory, Shop, ShoppingMall


class ItemAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_change = True
    confirmation_fields = ["price"]

    list_display = ("name", "price", "currency")
    readonly_fields = ["image_preview"]

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            return mark_safe('<img src="{obj.image.url}" />')


class InventoryAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ("shop", "item", "quantity")
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]


class ShopAdmin(AdminConfirmMixin, admin.ModelAdmin):
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


class ShoppingMallAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_add = True
    confirm_change = True
    confirmation_fields = ["name"]


admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(ShoppingMall, ShoppingMallAdmin)
