from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Category, Genre, Title, Review, Comment, CustomUser


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ('name', 'slug')


class TitleAdminForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = '__all__'

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and year > timezone.now().year:
            raise forms.ValidationError('Год не может быть больше текущего.')
        return year


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    form = TitleAdminForm
    list_display = ('name', 'year', 'category', 'get_genres')
    list_display_links = ('name',)
    list_editable = ('category',)
    list_filter = ('year', 'category', 'genre')
    search_fields = ('name', 'description')
    list_per_page = 20

    @admin.display(description='Жанры')
    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('text', 'author__username', 'title__name')
    date_hierarchy = 'pub_date'
    list_per_page = 20

    @admin.display(description='Текст')
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username', 'review__text')
    date_hierarchy = 'pub_date'
    list_per_page = 20

    @admin.display(description='Текст')
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    filter_horizontal = ('groups', 'user_permissions')
