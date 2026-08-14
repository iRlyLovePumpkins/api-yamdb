from rest_framework import filters
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from .utils import ALLOWED_METHODS


class CatalogModelMixin:
    """Миксин для категорий и жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ALLOWED_METHODS

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)


class NestedModelMixin:
    """Миксин для комментариев и ревью."""
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin,)
    http_method_names = ALLOWED_METHODS
