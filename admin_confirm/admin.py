
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.utils.translation import gettext as _


class AdminConfirmMixin(object):
    """Generic AdminConfirm Mixin"""

    change_needs_confirmation = False

    # Custom templates (designed to be over-ridden in subclasses)
    change_confirmation_template = None

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

    def change_view(self, request, object_id=None, form_url="", extra_context=None):
        # self.message_user(request, f"{request.POST}")
        if request.method == "POST" and request.POST.get("_change_needs_confirmation"):
            return self._change_confirmation_view(
                request, object_id, form_url, extra_context
            )

        extra_context = {
            **(extra_context or {}),
            'change_needs_confirmation': self.change_needs_confirmation
        }
        return super().change_view(request, object_id, form_url, extra_context)

    def _change_confirmation_view(self, request, object_id, form_url, extra_context):
        # Do we need any of this code?
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

        obj = self.get_object(request, unquote(object_id), to_field)

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )

        # Should we be validating the data here? Or just pass it to super?
        form = ModelForm(request.POST, request.FILES, obj)
        form_validated = form.is_valid()
        if form_validated:
            new_object = self.save_form(request, form, change=not add)
        else:
            new_object = form.instance

        if add:
            title = _("Add %s")
        elif self.has_change_permission(request, obj):
            title = _("Change %s")

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

        context = {
            **self.admin_site.each_context(request),
            "title": title % opts.verbose_name,
            "subtitle": str(obj),
            "object_name": str(obj),
            "object_id": object_id,
            "original": obj,
            "new_object": new_object,
            "app_label": opts.app_label,
            "model_name": opts.model_name,
            "opts": opts,
            "preserved_filters": self.get_preserved_filters(request),
            "form_data": form_data,
            "submit_name": save_action,
            **(extra_context or {}),
        }
        return self.render_change_confirmation(request, context)
