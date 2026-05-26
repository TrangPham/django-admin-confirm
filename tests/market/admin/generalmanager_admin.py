from django.contrib.admin import ModelAdmin
from admin_confirm.admin import AdminConfirmMixin, confirm_action


def external_action_no_confirmation(modeladmin, request, queryset):
    modeladmin.message_user(
        request, "This is an external action that should be imported and work without confirmation"
    )


@confirm_action
def external_action_with_confirmation(modeladmin, request, queryset):
    modeladmin.message_user(
        request, "This is an external action that should be imported and work with confirmation"
    )


class GeneralManagerAdmin(AdminConfirmMixin, ModelAdmin):
    save_as = True
    search_fields = ["name"]
    confirm_change = True
    confirm_add = True
    confirmation_fields = ["name", "headshot"]
    list_display = ["name", "email"]
    actions = [external_action_no_confirmation, external_action_with_confirmation]
    confirmation_actions = [external_action_with_confirmation]
