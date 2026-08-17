from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import exceptions, serializers

from reviews.models import Category, Comment, Genre, Review, Title

from .utils import validate_username_field

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate_username(self, value):
        """Не позволяет пользователю устанавливать имя 'me'."""
        return validate_username_field(value)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями"""
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами"""
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с произведениями"""
    rating = serializers.IntegerField(
        read_only=True,
        allow_null=True
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category', 'rating')
        read_only_fields = ('rating',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['genre'] = GenreSerializer(
            instance.genre.all(), many=True).data
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами"""
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """
        Проверяем, что пользователь не оставляет
        более одного отзыва на произведение
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            title_id = self.context.get('view').kwargs.get('title_id')

            if Review.objects.filter(
                author=request.user,
                title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с комментариями"""
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate_username(self, value):
        return validate_username_field(value)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        errors = {}

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            errors["username"] = [
                "Этот username уже занят другим пользователем."
            ]

        if user_by_email and user_by_email.username != username:
            errors["email"] = ["Этот email уже существует."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """Создает нового или возвращает
        существующего пользователя (без пароля)."""
        user, _ = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username or not confirmation_code:
            raise serializers.ValidationError(
                "Поля 'username' и 'confirmation_code' "
                "обязательны для заполнения."
            )

        user = User.objects.filter(username=username).first()
        if user is None:
            raise exceptions.NotFound("Пользователь не найден.")

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {"confirmation_code": "Неверный код подтверждения."}
            )

        data['user'] = user
        return data
