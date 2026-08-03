from rest_framework import viewsets, filters, mixins
from django.shortcuts import get_object_or_404
# from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
#                                         IsAuthenticated)
# from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Review, Category, Genre, Title
from .serializers import (CommentSerializer, CategorySerializer,
                          ReviewSerializer, GenreSerializer, TitleSerializer)
# from .permissions import AuthorOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = (AuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    # pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = (AuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_review(self):
        return get_object_or_404(ReviewViewSet,
                                 id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
