import re

from rest_framework import serializers

from api_yamdb.settings import NOT_ALLOWED_USERNAMES


def validate_username_field(value):
    """Не позволяет пользователю устанавливать имя 'me'."""
    pattern = r'^[\w.@+-]+\Z'

    if value.lower() in NOT_ALLOWED_USERNAMES:
        raise serializers.ValidationError(
            f"Имя пользователя не может быть '{value.lower()}'")

    if not re.match(pattern, value):
        raise serializers.ValidationError(
            'Username может содержать только буквы, цифры и символы'
        )
    return value


def is_admin(user):
    """
    Проверяет, является ли пользователь администратором,
    стаффом или суперпользователем.
    """
    if not user or not user.is_authenticated:
        return False
    return (
        user.is_superuser
        or user.is_staff
        or getattr(user, 'role', None) == 'admin'
    )