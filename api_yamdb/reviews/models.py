from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import year_validator
from api_yamdb.settings import (
    ADMIN,
    MAX_TEXT_CHARS,
    MODERATOR,
    ROLE_CHOICES,
    USER,
)


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
        return self.text[:MAX_TEXT_CHARS]


class CustomUser(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True)
    role = models.CharField(
        'Роль',
        blank=True,
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER)
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        blank=False,
        null=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class Genre(NameMixin, SlugMixin):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(NameMixin, SlugMixin):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(NameMixin):
    year = models.IntegerField(
        'Год выпуска',
        validators=[year_validator])
    description = models.TextField(
        'Описание',
        blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категория')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(BaseReviewModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author')]


class Comment(BaseReviewModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
