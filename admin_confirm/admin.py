from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.utils.translation import gettext as _

class AdminConfirmMixin(object):
    # Should we ask for confirmation for changes?
    confirm_change = None

    # Should we ask for confirmation for additions?
    confirm_add = None

    # If asking for confirmation, which fields should we confirm for?
    confirmation_fields = None

    # Custom templates (designed to be over-ridden in subclasses)
    change_confirmation_template = None

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

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST":
            if (not object_id and "_confirm_add" in request.POST) or (object_id and "_confirm_change"):
                return self._change_confirmation_view(request, object_id, form_url, extra_context)

        extra_context = {
            **(extra_context or {}),
            'confirm_add': self.confirm_add,
            'confirm_change': self.confirm_change
        }
        return super().changeform_view(request, object_id, form_url, extra_context)

    def _change_confirmation_view(self, request, object_id, form_url, extra_context):
        # This code is taken from super()._changeform_view
        to_field = request.POST.get(
            TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR)
        )
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
            self.message_user(request, add)
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
        form_validated = form.is_valid()
        if form_validated:
            new_object = self.save_form(request, form, change=not add)
        else:
            new_object = form.instance

        changed_data = {}
        if add:
            for name in form.changed_data:
                changed_data[name] = [None, new_object.__getattribute__(name)]
        else:
            # Parse the changed data - Note that using form.changed_data would not work as initial is not set
            for name, field in form.fields.items():
                initial_value = obj.__getattribute__(name)
                new_value = new_object.__getattribute__(name)
                if field.has_changed(initial_value, new_value) and initial_value != new_value:
                    changed_data[name] = [initial_value, new_value]

        changed_confirmation_fields = set(self.get_confirmation_fields(request, obj)) & set(changed_data.keys())
        self.message_user(request, changed_confirmation_fields)
        if not bool(changed_confirmation_fields):
            # No confirmation required for changed fields, continue to save
            return super()._changeform_view(request, object_id, form_url, extra_context)

        # Parse the original save action from request
        save_action = None
        for action in ["_save", "_saveasnew", "_addanother", "_continue"]:
            if action in request.POST:
                save_action = action
                break

        # Parse raw form data from POST
        form_data = {}
        for key in request.POST:
            if key.startswith("_") or key == 'csrfmiddlewaretoken':
                continue
            form_data[key] = request.POST.get(key)

        if add:
            title_action = _('adding')
        else:
            title_action = _('changing')

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
