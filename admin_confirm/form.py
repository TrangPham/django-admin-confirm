from contextlib import suppress
from typing import Dict
from django.db.models import FileField, ImageField
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


def get_changed_data(form: ModelForm) -> Dict:
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
        # No cover: This should never happen because the form should be bound when this function is called.
        raise FormNotBoundException("Form must be bound to get changed data")  # pragma: no cover

    model = form._meta.model
    changed_data = {}
    # Parse the changed data - Note that form.changed_data only returns
    # a list of the changed fields, not the old vs new values
    for name, new_value in form.cleaned_data.items():
        # Ignore custom fields
        with suppress(FieldDoesNotExist):
            if name not in form.changed_data:
                continue

            initial_value = form.initial.get(name)
            if initial_value == new_value:
                continue

            field_object = model._meta.get_field(name)
            changed_data[name] = display_for_changed_data(field_object, initial_value, new_value)

    return changed_data
