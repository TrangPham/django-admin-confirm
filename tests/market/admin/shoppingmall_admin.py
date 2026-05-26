"""ShoppingMallAdmin tests:
- confirm_add and confirm_change should work when inlines are present and with raw_id_fields
Note: Currently, the confirmation_fields only include fields from the main model, not from the inlines.
    This test ensures that the presence of inlines and raw_id_fields does not interfere with the confirmation process for the main model.
"""

from ..models import ShoppingMall
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import StackedInline
from admin_confirm.admin import AdminConfirmMixin


class ShopInline(StackedInline):
    model = ShoppingMall.shops.through


class ShoppingMallAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
    confirmation_fields = ["name"]

    inlines = [ShopInline]
    raw_id_fields = ["general_manager"]
