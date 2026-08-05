from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
# from .permissions import AuthorOrReadOnly
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title

from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)

from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                         IsAuthenticated, AllowAny)
# from rest_framework.pagination import LimitOffsetPagination


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    
    permission_classes = [IsAdminOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin)
    # pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin)

    def get_review(self):
        return get_object_or_404(ReviewViewSet,
                                 id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly)


class AuthViewSet(viewsets.GenericViewSet):  # Код с подтверждением будет в терминале
    """ViewSet для регистрации и получения токена через роутер."""
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