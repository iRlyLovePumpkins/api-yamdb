from rest_framework import filters
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import models

from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin)
from api_yamdb.settings import ALLOWED_METHODS


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


class SlugMixin(models.Model):
    """Миксин для моделей с полем Slug"""
    slug = models.SlugField(
        'Идентификатор',
        max_length=50,
        unique=True,
        db_index=True
    )

    class Meta:
        abstract = True


class NameMixin(models.Model):
    """Миксин для моделей с полем name"""
    name = models.CharField('Название', max_length=256)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseReviewModel(models.Model):
    """Абстрактная базовая модель для отзывов и комментов"""
    text = models.TextField('Текст')

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)

    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Автор')

    class Meta:
        abstract = True

    def __str__(self):
        return self.text
