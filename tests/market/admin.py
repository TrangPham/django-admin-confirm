from django.contrib import admin

from admin_confirm.admin import AdminConfirmMixin

from .models import Item, Inventory, Shop


class ItemAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'currency')
    require_change_confirmation = True


class InventoryAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('shop', 'item', 'quantity')
    requires_change_confirmation = {
        'fields': ['shop']
    }


class ShopAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)