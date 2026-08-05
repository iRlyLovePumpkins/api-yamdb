from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор или суперпользователь имеют полный доступ.
    Остальные (включая анонимов) — только чтение (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.is_staff or request.user.role == 'admin')
        )

class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам, суперпользователям или персоналу."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', None) == 'admin')
        )

class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Права на редактирование/удаление отзывов и комментариев:
    - Чтение доступно всем (безопасные методы).
    - Создание доступно любому аутентифицированному пользователю.
    - Изменение/удаление: Автор, Модератор, Администратор или Суперпользователь.
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
            request.user.is_superuser or
            request.user.is_staff or
            request.user.role == 'admin' or
            request.user.role == 'moderator' or
            obj.author == request.user
        )