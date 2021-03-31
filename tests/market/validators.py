from django.core.exceptions import ValidationError
from .constants import VALID_CURRENCIES


def validate_currency(value: str):
    currency_values = [c[0] for c in VALID_CURRENCIES]
    if value not in currency_values:
        raise ValidationError("Invalid Currency")
