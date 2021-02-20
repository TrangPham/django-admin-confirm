from django import template
from django.db.models.query import QuerySet

register = template.Library()


@register.filter
def format_change_data_field_value(field_value):
    if isinstance(field_value, QuerySet):
        return list(field_value)

    return field_value
