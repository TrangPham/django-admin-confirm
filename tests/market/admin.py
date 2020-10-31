from django.contrib import admin

from admin_confirm.admin import AdminConfirmMixin

from .models import Item, Inventory, Shop


class ItemAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'currency')
    change_needs_confirmation = True


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('shop', 'item', 'quantity')


class ShopAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)