from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated, AllowAny)
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, Comment
from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin, IsAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)

User = get_user_model()

ALLOWED_METHODS = ('get', 'post', 'patch', 'delete', 'head', 'options')


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdmin,)
    http_method_names = ALLOWED_METHODS

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return [IsAdmin()]

    @action(
        detail=False,
        methods=['get', 'patch', 'delete', 'put'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method in ['DELETE', 'PUT']:
            raise MethodNotAllowed(request.method)

        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if not (request.user.is_superuser
                or request.user.is_staff
                or getattr(request.user, 'role', None) == 'admin'):
            serializer.validated_data.pop('role', None)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin,)
    http_method_names = ALLOWED_METHODS

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin,)
    http_method_names = ALLOWED_METHODS

    def get_review(self):
        return get_object_or_404(Review,
                                 id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с категориями"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ALLOWED_METHODS

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с жанрами"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ALLOWED_METHODS

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(self.request.method)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с произведениями"""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('category', 'genre', 'name', 'year')
    lookup_field = 'id'
    http_method_names = ALLOWED_METHODS

    def get_queryset(self):
        queryset = super().get_queryset()

        category_slug = self.request.query_params.get('category')
        genre_slug = self.request.query_params.get('genre')
        name = self.request.query_params.get('name')
        year = self.request.query_params.get('year')

        if category_slug is not None:
            queryset = queryset.filter(category__slug=category_slug)
        if genre_slug is not None:
            queryset = queryset.filter(genre__slug=genre_slug)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if year is not None:
            queryset = queryset.filter(year=year)

        return queryset


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet для регистрации и получения токена через роутер."""
    # Код с подтверждением будет в терминале
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        """Эндпоинт: /api/v1/auth/signup/"""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Код подтверждения для YaMDB',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email='admin@yamdb.local',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {
                "email": user.email,
                "username": user.username
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='token')
    def token(self, request):
        """Эндпоинт: /api/v1/auth/token/"""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {"confirmation_code": "Неверный код подтверждения."},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {"token": str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
