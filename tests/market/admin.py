from django.contrib import admin

from admin_confirm.admin import AdminConfirmMixin

from .models import Item, Inventory, Shop


class ItemAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'currency')
    confirm_change = True


class InventoryAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('shop', 'item', 'quantity')
    confirm_change = True
    confirm_add = True
    confirmation_fields = ['shop']


class ShopAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirmation_fields = ['name']


admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
