from django.contrib import admin

from admin_confirm.admin import AdminConfirmMixin, confirm_action

from .models import Item, Inventory, Shop


class ItemAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ("name", "price", "currency")
    confirm_change = True


class InventoryAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ("shop", "item", "quantity")
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]


class ShopAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirmation_fields = ["name"]

    actions = ["show_message"]

    @confirm_action
    def show_message(modeladmin, request, queryset):
        shops = ", ".join(shop.name for shop in queryset)
        modeladmin.message_user(request, f"You selected: {shops}")



admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
