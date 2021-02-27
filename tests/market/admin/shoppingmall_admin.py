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
