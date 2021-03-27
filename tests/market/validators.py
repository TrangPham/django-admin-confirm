from .constants import VALID_CURRENCIES


def validate_currency(value: str) -> bool:
    currency_values = [c[0] for c in VALID_CURRENCIES]
    return value in currency_values
