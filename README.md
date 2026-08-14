# YaMDb

This repository contains a Django project using DRF: **Yandex MDb**
YaMDb — Your Movie & Book Review Hub
YaMDb is a Django REST Framework project that lets users share their opinions on movies, books, music, and more.

What is YaMDb?
Think of it as your personal review aggregator — a place where you can rate and discuss any creative work, from classic literature to underground music.

Important: YaMDb doesn't host any content. You can't watch movies or listen to music here — only read, rate, and review!

## How It Works
### Works
A work is anything you can review:
- Books — "Winnie‑the‑Pooh", "The Martian Chronicles"
- Movies — "Inception", "The Matrix"
- Music — "Davechya" by Zhuki, Bach's second suite
- Visual Arts or even Jewelry — the list is flexible!

### Categories
Works are grouped into categories like:
- Books
- Movies
- Music
- Visual Arts (you can add more!)

### Genres
Each work can have a genre from a predefined list:
- Fairy Tale
- Rock
- Art House
- Science Fiction
- And more...

### User Roles
```
**Role**              **Permissions**
Anonymous	            View works, reviews, and comments
Authenticated	        Everything above + write reviews, rate works, comment on others' reviews
Moderator	            All user permissions + delete any review or comment
Admin	                Full control — add works, categories, genres, manage users
```
## Rating System

Users rate works on a scale of 1 to 10.
Each user can leave only one review per work.
The average rating is calculated automatically based on all user scores.
Reviews can include detailed text feedback.

## Access Control

```
**Action**                              **Who Can Do It**
View works, reviews, comments	          Anyone (no authentication needed)
Write reviews & comments	              Authenticated users
Edit own reviews, comments                Author only
Delete any review or comment	          Moderator or Admin
Add works, categories, genres	          Admin only
Manage users	                          Admin only
```

## Features

- **Registration and authentication via JWT**
- **Creation, editing, and deletion of titles, reviews**
- **Commenting on reviews**
- **Grouping titles by genre, category**
- **Searching by subscriptions**
- **Paginating responses**

## Technology stack

- **Python** 3.12.7
- **Django** 6.1
- **Django REST Framework** 3.18
- **Djoser** - 2.3.1
- **JWT** - tokens
- **SQLite** - database

## Installing the project:
### Cloning repository:
git clone https://github.com/iRlyLovePumpkins/api-yamdb.git
### Сreating virtual environment:
```bash
python -3.12 -m venv venv
```
```bash 
. venv/bin/activate
```
### Install requirements:
```bash
pip install -r requirements.txt
```
### Make migrations:
```bash
cd api_yamdb
```
**❗❗❗In api_yamdb/api_yamdb❗❗❗**
```bash
py manage.py migrate
```

## Using the project:
### Start Server
**❗❗❗In api_yamdb/api_yamdb❗❗❗**
```bash
py manage.py runserver
```
### Tests:
**❗❗❗In api_yamdb❗❗❗**
```bash
pytest
```

## The structure of the project:
```text
postman_collection/     # Collection of postman requests
tests/                  # Project tests
api_yamdb/
├── api/
│   ├── __init__.py
│   ├── apps.py
│   ├── serializers.py  # Api Serializators
│   ├── validators.py   # Project validators
│   ├── mixins.py       # Project mixins
│   ├── filters.py      # Project filters
│   ├── urls.py         # Api endpoints
│   ├── views.py        # Api viewsets
│   └── permissions.py  # Api permissions classes
├── reviews/
│   ├── management/     # Project management folder
│   │   ├── __init__.py
│   │   └── commands/   # Project commands folder
│   │       ├── __init__.py
│   │       └── import_csv.py   # Command csv to db import
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   └── models.py      # Project models
├── api_yamdb/
│   ├── __init__.py
│   ├── settings.py    # Project settings
│   ├── urls.py        # Base urls
│   ├── asgi.py
│   └── wsgi.py
└── manage.py
requirements.txt
.gitignore
LICENSE
pytest.ini             # Setup pytests
README.md              # This file
setup.cfg              # Setup Flake 8
```

## API Endpoints
>The API provides the following main endpoints (**all under /api/v1/**):
```text
Method   Endpoint                                      Description
POST     /auth/signup/                                 Register a new user (get confirmation code)
POST     /auth/token/                                  Obtain JWT token (exchange username and confirmation_code)
GET      /categories/                                  Get list of all categories (public)
POST     /categories/                                  Create a new category (admin only)
DELETE   /categories/{slug}/                           Delete a category by slug (admin only)
GET      /genres/                                      Get list of all genres (public)
POST     /genres/                                      Create a new genre (admin only)
DELETE   /genres/{slug}/                               Delete a genre by slug (admin only)
GET      /titles/                                      Get list of all titles (public)
POST     /titles/                                      Create a new title (admin only)
GET      /titles/{titles_id}/                          Get title details by ID (public)
PATCH    /titles/{titles_id}/                          Partially update a title (admin only)
DELETE   /titles/{titles_id}/                          Delete a title by ID (admin only)
GET      /titles/{title_id}/reviews/                   Get list of all reviews for a title (public)
POST     /titles/{title_id}/reviews/                   Create a new review for a title (authenticated users)
GET      /titles/{title_id}/reviews/{review_id}/       Get a review by ID (public)
PATCH    /titles/{title_id}/reviews/{review_id}/       Partially update a review (author, moderator, admin)
DELETE   /titles/{title_id}/reviews/{review_id}/       Delete a review (author, moderator, admin)
GET      /titles/{title_id}/reviews/{review_id}/comments/  Get list of comments for a review (public)
POST     /titles/{title_id}/reviews/{review_id}/comments/  Add a comment to a review (authenticated users)
GET      /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/  Get a comment by ID (public)
PATCH    /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/  Partially update a comment (author, moderator, admin)
DELETE   /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/  Delete a comment (author, moderator, admin)
GET      /users/                                       Get list of all users (admin only)
POST     /users/                                       Create a new user (admin only)
GET      /users/{username}/                            Get user by username (admin only)
PATCH    /users/{username}/                            Update user data by username (admin only)
DELETE   /users/{username}/                            Delete user by username (admin only)
GET      /users/me/                                    Get current user's profile data (authenticated users)
PATCH    /users/me/                                    Update current user's profile data (authenticated users)
```

## Request Examples
### 1. Register a New User
POST http://127.0.0.1:8000/api/v1/auth/signup/

```json
{
    "email": "user@example.com",
    "username": "testuser"
}
```
Response:

```json
{
    "email": "user@example.com",
    "username": "testuser"
}
```
### 2. Obtain JWT Token
POST http://127.0.0.1:8000/api/v1/auth/token/

```json
{
    "username": "testuser",
    "confirmation_code": "your-confirmation-code"
}
```
Response:

```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
### 3. Get List of Titles (Public)
GET http://127.0.0.1:8000/api/v1/titles/?category=action&year=2022

Response:

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Inception",
            "year": 2010,
            "rating": 8.5,
            "description": "A mind-bending thriller",
            "genre": [{"name": "Sci-Fi", "slug": "sci-fi"}],
            "category": {"name": "Action", "slug": "action"}
        }
    ]
}
```
### 4. Create a New Review
POST http://127.0.0.1:8000/api/v1/titles/1/reviews/

Authorization: Bearer <access_token>

```json
{
    "text": "Amazing movie!",
    "score": 9
}
```
Response:

```json
{
    "id": 1,
    "text": "Amazing movie!",
    "author": "testuser",
    "score": 9,
    "pub_date": "2025-01-01T12:00:00Z"
}
```
### 5. Add a Comment to a Review
POST http://127.0.0.1:8000/api/v1/titles/1/reviews/1/comments/

Authorization: Bearer <access_token>

```json
{
    "text": "I agree with this review!"
}
```
Response:

```json
{
    "id": 1,
    "text": "I agree with this review!",
    "author": "testuser",
    "pub_date": "2025-01-01T12:05:00Z"
}
```
### 6. Get Current User Profile
GET http://127.0.0.1:8000/api/v1/users/me/

Authorization: Bearer <access_token>

Response:

```json
{
    "username": "testuser",
    "email": "user@example.com",
    "first_name": "",
    "last_name": "",
    "bio": "",
    "role": "user"
}
```
### 7. Update Current User Profile
PATCH http://127.0.0.1:8000/api/v1/users/me/

Authorization: Bearer <access_token>

```json
{
    "first_name": "Test",
    "last_name": "User",
    "bio": "Software developer"
}
```
Response:

```json
{
    "username": "testuser",
    "email": "user@example.com",
    "first_name": "Test",
    "last_name": "User",
    "bio": "Software developer",
    "role": "user"
}
```
### 8. Create a New Category (Admin only)
POST http://127.0.0.1:8000/api/v1/categories/

Authorization: Bearer <access_token>

```json
{
    "name": "Comedy",
    "slug": "comedy"
}
```
Response:

```json
{
    "name": "Comedy",
    "slug": "comedy"
}
```
## Authors
```
Gkhali Aleksandra - teamlead
Falin Daniil      - backend
Tonevickaya Anna  - backend
```

## License
This project is distributed under the MIT license.
