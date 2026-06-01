from contextlib import suppress
from typing import Dict
from django.db.models import ManyToManyField, FileField, ImageField
from django.core.exceptions import FieldDoesNotExist
from django.forms import ModelForm
from .exceptions import FormNotBoundException

# Methods relating to ModelForm


def display_for_changed_data(field, initial_value, new_value):
    """What to display for the changed field on confirmation page"""
    if not isinstance(field, (FileField, ImageField)):
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


def get_changed_data(form: ModelForm, add: bool) -> Dict:
    """
    Given a form, detect the changes on the form from the default values (if add) or
    from the database values of the object (model instance)

    form - Submitted form that is attempting to alter the obj
    model - the model class of the obj
    obj - instance of model which is being altered
    add - are we attempting to add the obj or does it already exist in the database

    Returns a dictionary of the fields and their changed values if any
    """

    if not form.is_bound:
        raise FormNotBoundException("Form must be bound to get changed data")

    model = form._meta.model
    obj = form.instance
    changed_data = {}
    if add:
        for name, new_value in form.cleaned_data.items():
            # Ignore custom fields
            with suppress(FieldDoesNotExist):
                # Don't consider default values as changed for adding
                field_object = model._meta.get_field(name)
                default_value = field_object.get_default()
                if (
                    name in form.changed_data
                    and new_value is not None  # defaults to default value
                    and new_value != default_value
                ):
                    # Show what the default value is
                    changed_data[name] = display_for_changed_data(
                        field_object, default_value, new_value
                    )
    else:
        # Parse the changed data - Note that form.changed_data only returns
        # a list of the changed fields, not the old vs new values
        for name, new_value in form.cleaned_data.items():
            # Ignore custom fields
            with suppress(FieldDoesNotExist):

                field_object = model._meta.get_field(name)

                if isinstance(field_object, ManyToManyField):
                    initial_value = field_object.value_from_object(obj)
                    if name in form.changed_data:
                        changed_data[name] = display_for_changed_data(
                            field_object, initial_value, new_value
                        )
                else:
                    initial_value = form.initial.get(name)
                    if name in form.changed_data:
                        changed_data[name] = display_for_changed_data(
                            field_object, initial_value, new_value
                        )
                if initial_value != form.initial.get(name):
                    raise ValueError(f"{initial_value} vs {form.initial.get(name)} for name {name}")

    if not changed_data and form.has_changed():
        raise ValueError("123")

    return changed_data
