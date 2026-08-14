from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = [
    (USER, 'User'),
    (MODERATOR, 'Moderator'),
    (ADMIN, 'Admin'),
]


class CustomUser(AbstractUser):
    USER = USER
    MODERATOR = MODERATOR
    ADMIN = ADMIN

    ROLE_CHOICES = ROLE_CHOICES

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        blank=True,
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER
    )
    email = models.EmailField(unique=True, blank=False, null=False)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username


class BaseSlugModel(models.Model):
    """Абстрактная базовая модель для категорий и жанров."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Genre(BaseSlugModel):
    """Модель жанра."""
    pass


class Category(BaseSlugModel):
    """Модель категории."""
    pass


def validate_year(value):
    """
    Валидатор для проверки, что год не превышает текущий.
    """
    current_year = timezone.now().year
    if value > current_year:
        raise models.ValidationError(
            f'Год не может быть больше {current_year}.'
        )
    return value


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=[validate_year])
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review_for_user'
            )
        ]
        ordering = ['-pub_date']

    def __str__(self):
        return f'Отзыв от {self.author.username} на {self.title.name}'


class Comment(models.Model):
    """Модель комментария."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return f'Комментарий от {self.author.username} к отзыву {self.review.id}'
 