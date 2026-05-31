from django.contrib import admin

from .site_wide_action import (
    site_wide_confirm_action,
    site_wide_no_confirm_action,
)

from ..models import (
    GeneralManager,
    Item,
    Inventory,
    ItemSale,
    Shop,
    ShoppingMall,
    Transaction,
    Checkout,
    Consumer,
)

from .item_admin import ItemAdmin
from .inventory_admin import InventoryAdmin
from .shop_admin import ShopAdmin
from .shoppingmall_admin import ShoppingMallAdmin
from .generalmanager_admin import GeneralManagerAdmin
from .item_sale_admin import ItemSaleAdmin
from .transaction_admin import TransactionAdmin
from .checkout_admin import CheckoutAdmin
from .consumer_admin import ConsumerAdmin

admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(ShoppingMall, ShoppingMallAdmin)
admin.site.register(GeneralManager, GeneralManagerAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ItemSale, ItemSaleAdmin)
admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Consumer, ConsumerAdmin)
admin.site.add_action(site_wide_no_confirm_action)
admin.site.add_action(site_wide_confirm_action)
