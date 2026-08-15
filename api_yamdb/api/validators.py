import datetime

from django.core.exceptions import ValidationError


def year_validator(value):
    """Проверяет, что год не больше текущего года."""
    current_year = datetime.datetime.now().year
    if value > current_year:
        raise ValidationError(f'{value} - это будущее!',
                              params={'value': value}
                              )
