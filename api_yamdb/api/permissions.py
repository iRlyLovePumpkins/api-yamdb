from rest_framework import permissions
from reviews.models import MODERATOR
from .utils import is_admin


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам,
    суперпользователям или персоналу."""
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsAdminOrReadOnly(IsAdmin):
    """
    Администратор или суперпользователь имеют полный доступ.
    Остальные (включая анонимов) — только чтение (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsAuthorOrModeratorOrAdmin(IsAdmin):
    """
    Права на редактирование/удаление отзывов и комментариев:
    - Чтение доступно всем (безопасные методы).
    - Создание доступно любому аутентифицированному пользователю.
    - Изменение/удаление: Автор, Модератор,
    Администраторили Суперпользователь.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False

        return (
            obj.author == request.user
            or request.user.role == MODERATOR
            or super().has_permission(request, view)
        )
