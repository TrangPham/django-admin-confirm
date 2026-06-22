"""ConsumerAdmin tests:
- confirm_change should work with pk which have "_" in them
"""

from django.contrib import admin
from admin_confirm.admin import AdminConfirmMixin
from ..models import Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


class ConsumerAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ["id", "name", "email"]
    search_fields = ["name", "email"]
    fieldsets = (("Basic Information", {"fields": ("name", "email")}),)

    confirm_change = True
    confirmation_fields = ["name"]
    inlines = [TransactionInline]
