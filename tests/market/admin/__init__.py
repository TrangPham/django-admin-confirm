from django.contrib import admin

from ..models import GeneralManager, Item, Inventory, Shop, ShoppingMall

from .item_admin import ItemAdmin
from .inventory_admin import InventoryAdmin
from .shop_admin import ShopAdmin
from .shoppingmall_admin import ShoppingMallAdmin
from .generalmanager_admin import GeneralManagerAdmin

admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(ShoppingMall, ShoppingMallAdmin)
admin.site.register(GeneralManager, GeneralManagerAdmin)
