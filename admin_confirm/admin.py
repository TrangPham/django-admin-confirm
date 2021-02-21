from typing import Dict
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.utils.translation import gettext as _
from django.contrib.admin import helpers
from django.db.models import Model, ManyToManyField
from django.forms import ModelForm
from admin_confirm.utils import snake_to_title_case

SAVE_ACTIONS = ["_save", "_saveasnew", "_addanother", "_continue"]


class AdminConfirmMixin:
    # Should we ask for confirmation for changes?
    confirm_change = None

    # Should we ask for confirmation for additions?
    confirm_add = None

    # If asking for confirmation, which fields should we confirm for?
    confirmation_fields = None

    # Custom templates (designed to be over-ridden in subclasses)
    change_confirmation_template = None
    action_confirmation_template = None

    def get_confirmation_fields(self, request, obj=None):
        """
        Hook for specifying confirmation fields
        """
        if self.confirmation_fields is not None:
            return self.confirmation_fields

        return flatten_fieldsets(self.get_fieldsets(request, obj))

    def render_change_confirmation(self, request, context):
        opts = self.model._meta
        app_label = opts.app_label

        request.current_app = self.admin_site.name
        context.update(
            media=self.media,
        )

        return TemplateResponse(
            request,
            self.change_confirmation_template
            or [
                "admin/{}/{}/change_confirmation.html".format(
                    app_label, opts.model_name
                ),
                "admin/{}/change_confirmation.html".format(app_label),
                "admin/change_confirmation.html",
            ],
            context,
        )

    def render_action_confirmation(self, request, context):
        opts = self.model._meta
        app_label = opts.app_label

        request.current_app = self.admin_site.name
        context.update(
            media=self.media,
            opts=opts,
        )

        return TemplateResponse(
            request,
            self.action_confirmation_template
            or [
                "admin/{}/{}/action_confirmation.html".format(
                    app_label, opts.model_name
                ),
                "admin/{}/action_confirmation.html".format(app_label),
                "admin/action_confirmation.html",
            ],
            context,
        )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST":
            if (not object_id and "_confirm_add" in request.POST) or (
                object_id and "_confirm_change" in request.POST
            ):
                return self._change_confirmation_view(
                    request, object_id, form_url, extra_context
                )

        extra_context = {
            **(extra_context or {}),
            "confirm_add": self.confirm_add,
            "confirm_change": self.confirm_change,
        }
        return super().changeform_view(request, object_id, form_url, extra_context)

    def _get_changed_data(
        self, form: ModelForm, model: Model, obj: object, add: bool
    ) -> Dict:
        """
        Given a form, detect the changes on the form from the default values (if add) or
        from the database values of the object (model instance)

        form - Submitted form that is attempting to alter the obj
        model - the model class of the obj
        obj - instance of model which is being altered
        add - are we attempting to add the obj or does it already exist in the database

        Returns a dictionary of the fields and their changed values if any
        """
        changed_data = {}
        if form.is_valid():
            if add:
                for name, new_value in form.cleaned_data.items():
                    # Don't consider default values as changed for adding
                    default_value = model._meta.get_field(name).get_default()
                    if new_value is not None and new_value != default_value:
                        # Show what the default value is
                        changed_data[name] = [default_value, new_value]
            else:
                # Parse the changed data - Note that using form.changed_data would not work because initial is not set
                for name, new_value in form.cleaned_data.items():
                    # Since the form considers initial as the value first shown in the form
                    # It could be incorrect when user hits save, and then hits "No, go back to edit"
                    obj.refresh_from_db()
                    # Note: getattr does not work on ManyToManyFields
                    field_object = model._meta.get_field(name)
                    initial_value = getattr(obj, name)
                    if isinstance(field_object, ManyToManyField):
                        initial_value = field_object.value_from_object(obj)

                    if initial_value != new_value:
                        changed_data[name] = [initial_value, new_value]

        return changed_data

    def _get_form_data(self, request):
        """
        Parses the request post params into a format that can be used for the hidden form on the
        change confirmation page.
        """
        query_dict = request.POST.copy()
        # Note: Do not use QueryDict.get(), it returns only the last value for multivalues

        for key in SAVE_ACTIONS + [
            "_confirm_change",
            "_confirm_add",
            "csrfmiddlewaretoken",
        ]:
            if query_dict.get(key):
                query_dict.pop(key)

        form_data = []
        for k, v in query_dict.lists():
            if isinstance(v, list):
                for value in v:
                    form_data.append((k, value))
            else:
                form_data.append((k, v))

        # form_data = [(k, v) for k, v in form_data.lists()]
        return form_data

    def _change_confirmation_view(self, request, object_id, form_url, extra_context):
        # This code is taken from super()._changeform_view
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        model = self.model
        opts = model._meta

        add = object_id is None
        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied

            obj = None
        else:
            obj = self.get_object(request, unquote(object_id), to_field)
            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

            if not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )

        form = ModelForm(request.POST, request.FILES, obj)
        # End code from super()._changeform_view

        changed_data = self._get_changed_data(form, model, obj, add)

        changed_confirmation_fields = set(
            self.get_confirmation_fields(request, obj)
        ) & set(changed_data.keys())
        if not bool(changed_confirmation_fields):
            # No confirmation required for changed fields, continue to save
            return super()._changeform_view(request, object_id, form_url, extra_context)

        # Parse raw form data from POST
        form_data = self._get_form_data(request)
        # Parse the original save action from request
        save_action = None
        for key in request.POST.keys():
            if key in SAVE_ACTIONS:
                save_action = key
                break

        title_action = _("adding") if add else _("changing")

        context = {
            **self.admin_site.each_context(request),
            "preserved_filters": self.get_preserved_filters(request),
            "title": f"{_('Confirm')} {title_action} {opts.verbose_name}",
            "subtitle": str(obj),
            "object_name": str(obj),
            "object_id": object_id,
            "app_label": opts.app_label,
            "model_name": opts.model_name,
            "opts": opts,
            "form_data": form_data,
            "changed_data": changed_data,
            "add": add,
            "submit_name": save_action,
            **(extra_context or {}),
        }
        return self.render_change_confirmation(request, context)


def confirm_action(func):
    """
    @confirm_action function wrapper for Django ModelAdmin actions
    Will redirect to a confirmation page to ask for confirmation

    Next, it would call the action if confirmed. Otherwise, it would
    return to the changelist without performing action.
    """

    def func_wrapper(modeladmin, request, queryset):
        # First called by `Go` which would not have confirm_action in params
        if request.POST.get("_confirm_action"):
            return func(modeladmin, request, queryset)

        # get_actions will only return the actions that are allowed
        has_perm = modeladmin.get_actions(request).get(func.__name__) is not None

        action_display_name = snake_to_title_case(func.__name__)
        title = f"Confirm Action: {action_display_name}"

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": title,
            "queryset": queryset,
            "has_perm": has_perm,
            "action": func.__name__,
            "action_display_name": action_display_name,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "submit_name": "confirm_action",
        }

        # Display confirmation page
        return modeladmin.render_action_confirmation(request, context)

    return func_wrapper
