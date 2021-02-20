from django import template
from django.db.models.query import QuerySet
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_change_data_field_value(field_value):
    if isinstance(field_value, str):
        return field_value
    try:
        output = "<ul>"
        for value in iter(field_value):
            output += "<li>" + escape(value) + "</li>"
        output += "</ul>"
        return mark_safe(output)
    except:
        return field_value

    # if isinstance(field_value, QuerySet):
    #     return list(field_value)

    # return field_value
