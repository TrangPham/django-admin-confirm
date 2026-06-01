"""ConsumerAdmin tests:
- confirm_change should work with pk which have "_" in them
"""

from django.contrib import admin
from admin_confirm.admin import AdminConfirmMixin, InlineAdminConfirmMixin
from ..models import Transaction


class TransactionInline(InlineAdminConfirmMixin, admin.StackedInline):
    model = Transaction
    extra = 0
    confirm_change = True
    confirm_add = False


class ConsumerAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ["id", "name", "email"]
    search_fields = ["name", "email"]
    fieldsets = (("Basic Information", {"fields": ("name", "email")}),)

    confirm_change = True
    confirmation_fields = ["name"]
    inlines = [TransactionInline]
