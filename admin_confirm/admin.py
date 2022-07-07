import functools
from typing import Dict
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.utils.translation import gettext as _
from django.contrib.admin import helpers
from django.db.models import Model, ManyToManyField, FileField, ImageField
from django.forms import ModelForm
from django.utils.decorators import method_decorator
from admin_confirm.utils import (
    log,
    get_admin_change_url,
    snake_to_title_case,
    format_cache_key,
)
from django.views.decorators.cache import cache_control
from admin_confirm.constants import (
    CONFIRMATION_RECEIVED,
    CONFIRM_ADD,
    CONFIRM_CHANGE,
    SAVE,
    SAVE_ACTIONS,
    CACHE_KEYS,
    SAVE_AND_CONTINUE,
    SAVE_AS_NEW,
    CACHE_TIMEOUT,
)
from admin_confirm.file_cache import FileCache


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

    _file_cache = FileCache()

    def get_confirmation_fields(self, request, obj=None):
        """
        Hook for specifying confirmation fields
        """
        if self.confirmation_fields is not None:
            return self.confirmation_fields

        model_fields = set([field.name for field in self.model._meta.fields])
        admin_fields = set(flatten_fieldsets(self.get_fieldsets(request, obj)))
        return list(model_fields & admin_fields)

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

    @method_decorator(cache_control(private=True))
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST":
            if (not object_id and CONFIRM_ADD in request.POST) or (
                object_id and CONFIRM_CHANGE in request.POST
            ):
                log("confirmation is asked for")
                self._file_cache.delete_all()
                cache.delete_many(CACHE_KEYS.values())
                return self._change_confirmation_view(
                    request, object_id, form_url, extra_context
                )
            elif CONFIRMATION_RECEIVED in request.POST:
                return self._confirmation_received_view(
                    request, object_id, form_url, extra_context
                )
            else:
                self._file_cache.delete_all()
                cache.delete_many(CACHE_KEYS.values())

        extra_context = self._add_confirmation_options_to_extra_context(extra_context)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def _add_confirmation_options_to_extra_context(self, extra_context):
        log(
            f"Adding confirmation to extra_content {self.confirm_add} {self.confirm_change}"
        )
        return {
            **(extra_context or {}),
            "confirm_add": self.confirm_add,
            "confirm_change": self.confirm_change,
        }

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

        def _display_for_changed_data(field, initial_value, new_value):
            if not (isinstance(field, FileField) or isinstance(field, ImageField)):
                return [initial_value, new_value]

            if initial_value:
                if new_value is False:
                    # Clear has been selected
                    return [initial_value.name, None]
                elif new_value:
                    return [initial_value.name, new_value.name]
                else:
                    # No cover: Technically doesn't get called in current code because
                    # This function is only called if there was a difference in the data
                    return [initial_value.name, initial_value.name]  # pragma: no cover

            if new_value:
                return [None, new_value.name]

            return [None, None]

        changed_data = {}
        if add:
            for name, new_value in form.cleaned_data.items():
                # Don't consider default values as changed for adding
                field_object = model._meta.get_field(name)
                default_value = field_object.get_default()
                if new_value is not None and new_value != default_value:
                    # Show what the default value is
                    changed_data[name] = _display_for_changed_data(
                        field_object, default_value, new_value
                    )
        else:
            # Parse the changed data - Note that using form.changed_data would not work because initial is not set
            for name, new_value in form.cleaned_data.items():

                # Since the form considers initial as the value first shown in the form
                # It could be incorrect when user hits save, and then hits "No, go back to edit"
                obj.refresh_from_db()

                field_object = model._meta.get_field(name)
                initial_value = getattr(obj, name)

                # Note: getattr does not work on ManyToManyFields
                if isinstance(field_object, ManyToManyField):
                    initial_value = field_object.value_from_object(obj)

                if initial_value != new_value:
                    changed_data[name] = _display_for_changed_data(
                        field_object, initial_value, new_value
                    )

        return changed_data

    def _confirmation_received_view(self, request, object_id, form_url, extra_context):
        """
        When the form is a multipart form, the object and POST are cached
        This is required because file(s) cannot be programmically uploaded
        ie. There is no way to set a file on the html form

        If the form isn't multipart, this function would not be called.
        If there are no file changes, do nothing to the request and send to Django.

        If there are files uploaded, save the files from cached object to either:
        - the object instance if already exists
        - or save the new object and modify the request from `add` to `change`
        and pass the request to Django
        """
        log("Confirmation has been received")

        def _reconstruct_request_files():
            """
            Reconstruct the file(s) from the file cache (if any).
            Returns a dictionary of field name to cached file
            """
            reconstructed_files = {}

            cached_object = cache.get(CACHE_KEYS["object"])
            # Reconstruct the files from cached object
            if not cached_object:
                log("Warning: no cached_object")
                return

            if type(cached_object) != self.model:
                # Do not use cache if the model doesn't match this model
                log(f"Warning: cached_object is not of type {self.model}")
                return

            query_dict = request.POST

            for field in self.model._meta.get_fields():
                if not (isinstance(field, FileField) or isinstance(field, ImageField)):
                    continue

                cached_file = self._file_cache.get(
                    format_cache_key(model=self.model.__name__, field=field.name)
                )

                # If a file was uploaded, the field is omitted from the POST since it's in request.FILES
                if not query_dict.get(field.name):
                    if not cached_file:
                        log(
                            f"Warning: Could not find file cached for field {field.name}"
                        )
                    else:
                        reconstructed_files[field.name] = cached_file

            return reconstructed_files

        reconstructed_files = _reconstruct_request_files()
        if reconstructed_files:
            log(f"Found reconstructed files for fields: {reconstructed_files.keys()}")
            obj = None

            # remove the _confirm_add and _confirm_change from post
            modified_post = request.POST.copy()
            if CONFIRM_ADD in modified_post:
                del modified_post[CONFIRM_ADD]  # pragma: no cover
            if CONFIRM_CHANGE in modified_post:
                del modified_post[CONFIRM_CHANGE]  # pragma: no cover

            if object_id and SAVE_AS_NEW not in request.POST:
                # Update the obj with the new uploaded files
                # then pass rest of changes to Django
                obj = self.model.objects.filter(id=object_id).first()
            else:
                # Create the obj and pass the rest as changes to Django
                # (Since we are not handling the formsets/inlines)
                # Note that this results in the "Yes, I'm Sure" submission
                #   act as a `change` not an `add`
                obj = cache.get(CACHE_KEYS["object"])

            # No cover: __reconstruct_request_files currently checks for cached obj so obj won't be None
            if obj:  # pragma: no cover
                for field, file in reconstructed_files.items():
                    log(f"Setting file field {field} to file {file}")
                    setattr(obj, field, file)
                obj.save()
                object_id = str(obj.id)
                # Update the request path, used in the message to user and redirect
                # Used in `self.response_change`
                request.path = get_admin_change_url(obj)

                if SAVE_AS_NEW in request.POST:
                    # We have already saved the new object
                    # So change action to _continue
                    del modified_post[SAVE_AS_NEW]
                    if self.save_as_continue:
                        modified_post[SAVE_AND_CONTINUE] = True
                    else:
                        modified_post[SAVE] = True
                    if "id" in modified_post:
                        del modified_post["id"]
                        modified_post["id"] = object_id

            request.POST = modified_post

        self._file_cache.delete_all()
        cache.delete_many(CACHE_KEYS.values())

        return super()._changeform_view(request, object_id, form_url, extra_context)

    def _get_cleared_fields(self, request):
        """
        Checks for any ImageField or FileField which have been cleared by user.

        Because the form that is generated by Django for the model, would not have the
        `<field>-clear` inputs in them, they have to be injected into the hidden form
        on the confirmation page.
        """
        return [
            input_name.split("-clear")[0]
            for input_name in request.POST.keys()
            if input_name.endswith("-clear")
        ]

    def _change_confirmation_view(self, request, object_id, form_url, extra_context):
        # This code is taken from super()._changeform_view
        # https://github.com/django/django/blob/master/django/contrib/admin/options.py#L1575-L1592
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        model = self.model
        opts = model._meta

        if SAVE_AS_NEW in request.POST:
            object_id = None

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

        form = ModelForm(request.POST, request.FILES, instance=obj)
        form_validated = form.is_valid()
        if form_validated:
            new_object = self.save_form(request, form, change=not add)
        else:
            new_object = form.instance
        formsets, inline_instances = self._create_formsets(
            request, new_object, change=not add
        )
        # End code from super()._changeform_view
        # form.is_valid() checks both errors and "is_bound"
        # If form has errors, show the errors on the form instead of showing confirmation page
        if not form_validated:
            log("Invalid Form: return early")
            log(form.errors)
            # We must ensure that we ask for confirmation when showing errors
            extra_context = self._add_confirmation_options_to_extra_context(
                extra_context
            )
            return super()._changeform_view(request, object_id, form_url, extra_context)

        add_or_new = add or SAVE_AS_NEW in request.POST
        # Get changed data to show on confirmation
        changed_data = self._get_changed_data(form, model, obj, add_or_new)

        changed_confirmation_fields = set(
            self.get_confirmation_fields(request, obj)
        ) & set(changed_data.keys())
        if not bool(changed_confirmation_fields):
            log("No change detected")
            # No confirmation required for changed fields, continue to save
            return super()._changeform_view(request, object_id, form_url, extra_context)

        # Parse the original save action from request
        save_action = None
        # No cover: There would not be a case of not request.POST.keys() and form is valid
        for key in request.POST.keys():  # pragma: no cover
            if key in SAVE_ACTIONS:
                save_action = key
                break

        cleared_fields = []
        if form.is_multipart():
            log("Caching files")
            cache.set(CACHE_KEYS["object"], new_object, CACHE_TIMEOUT)

            # Save files as tempfiles
            for field_name in request.FILES:
                file = request.FILES[field_name]
                self._file_cache.set(
                    format_cache_key(model=model.__name__, field=field_name), file
                )

            # Handle when files are cleared - since the `form` object would not hold that info
            cleared_fields = self._get_cleared_fields(request)

        log("Render Change Confirmation")
        title_action = _("adding") if add_or_new else _("changing")
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
            "obj": obj,
            "changed_data": changed_data,
            "add": add,
            "save_as_new": SAVE_AS_NEW in request.POST,
            "submit_name": save_action,
            "form": form,
            "cleared_fields": cleared_fields,
            "formsets": formsets,
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

    @functools.wraps(func)
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
