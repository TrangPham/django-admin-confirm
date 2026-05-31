from django.contrib import admin
from admin_confirm.admin import confirm_action


@admin.action(description="Site wide no confirm action")
def site_wide_no_confirm_action(modeladmin, request, queryset):
    modeladmin.message_user(request, "Did action:site wide no confirm action")


@confirm_action
@admin.action(description="Site wide confirm action")
def site_wide_confirm_action(modeladmin, request, queryset):
    modeladmin.message_user(request, "Did action:site wide confirm action")
