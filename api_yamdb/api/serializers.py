import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

from api_yamdb.settings import NOT_ALLOWED_USERNAMES

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями"""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с произведениями"""
    rating = serializers.SerializerMethodField()

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        read_only_fields = ('rating',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(
            instance.category).data
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
        # read_only_fields = ('author',)


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
        # read_only_fields = ('author', 'post')


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate_username(self, value):
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

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {"username": "Этот username уже занят другим пользователем."})
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError({"email":
                                               "Этот email уже существует."})

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
