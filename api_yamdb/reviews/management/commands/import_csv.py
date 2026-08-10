import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


class Command(BaseCommand):
    """Импорт данных из CSV-файлов в базу данных."""

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        simple_files = [
            ('users.csv', CustomUser),
            ('category.csv', Category),
            ('genre.csv', Genre),
        ]

        for filename, model in simple_files:
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(f'Файл {filename} не найден, пропускаем...')
                )
                continue

            self.stdout.write(f'Импорт данных из {filename}...')
            with open(file_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    model.objects.get_or_create(**row)

        titles_path = os.path.join(data_dir, 'titles.csv')
        if os.path.exists(titles_path):
            self.stdout.write('Импорт данных из titles.csv...')
            with open(titles_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    category_id = row.get('category') or row.get('category_id')
                    category = Category.objects.get(pk=category_id)

                    Title.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'year': row['year'],
                            'category': category,
                        },
                    )

        genre_title_path = os.path.join(data_dir, 'genre_title.csv')
        if os.path.exists(genre_title_path):
            self.stdout.write('Импорт связей из genre_title.csv...')
            with open(genre_title_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    title = Title.objects.get(pk=row['title_id'])
                    genre = Genre.objects.get(pk=row['genre_id'])
                    title.genre.add(genre)

        reviews_path = os.path.join(data_dir, 'review.csv')
        if os.path.exists(reviews_path):
            self.stdout.write('Импорт данных из review.csv...')
            with open(reviews_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    title = Title.objects.get(pk=row['title_id'])
                    author_key = (
                        'author' if 'author' in row else 'user'
                    )
                    author = CustomUser.objects.get(pk=row[author_key])

                    Review.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'title': title,
                            'text': row['text'],
                            'author': author,
                            'score': row['score'],
                            'pub_date': row['pub_date'],
                        },
                    )

        comments_path = os.path.join(data_dir, 'comments.csv')
        if os.path.exists(comments_path):
            self.stdout.write('Импорт данных из comments.csv...')
            with open(comments_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    review = Review.objects.get(pk=row['review_id'])
                    author_key = (
                        'author' if 'author' in row else 'user'
                    )
                    author = CustomUser.objects.get(pk=row[author_key])

                    Comment.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'review': review,
                            'text': row['text'],
                            'author': author,
                            'pub_date': row['pub_date'],
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS('Все данные успешно импортированы!')
        )