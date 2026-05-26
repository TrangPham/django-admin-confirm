"""ItemSaleAdmin tests:
- confirm_add and confirm_change should work with default settings
This is a basic test to ensure that the confirmation process works with the default settings of the AdminConfirmMixin, without any custom configuration.
"""

from admin_confirm.admin import AdminConfirmMixin


from django.contrib.admin import ModelAdmin


class ItemSaleAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
