"""ShoppingMallAdmin tests:
- confirm_add and confirm_change should work when inlines are present and with raw_id_fields
- default confirmation_fields should include inlines and trigger confirmation when M2M field changes
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
    confirmation_fields = "__all__"

    inlines = [ShopInline]
    raw_id_fields = ["general_manager"]
