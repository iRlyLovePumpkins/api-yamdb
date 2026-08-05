from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

# from rest_framework.validators import UniqueTogetherValidator


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
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
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя пользователя не может быть 'me'.")
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError({"username": "Этот username уже занят другим пользователем."})
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError({"email": "Этот email уже существует."})

        return data

    def create(self, validated_data):
        """Создает нового или возвращает существующего пользователя (без пароля)."""
        user, _ = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)