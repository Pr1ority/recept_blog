![Workflow Status](https://github.com/Pr1ority/foodgram/actions/workflows/main.yml/badge.svg?branch=main)

## Описание проекта

Recept Blog — это веб-приложение, которое позволяет пользователям публиковать рецепты, делиться ими с другими, добавлять рецепты в избранное и формировать списки покупок на основе ингредиентов. Также есть возможность подписываться на других пользователей, отслеживать их рецепты и управлять избранным.

## Автор

Бондаренко Алексей Олегович
- Telegram: [@alovsemprivet](https://t.me/alovsemprivet)
- GitHub: [Pr1ority](https://github.com/Pr1ority)

## Технологический стек

- Backend: Django, Django REST Framework
- Web server: Nginx
- Application server: Gunicorn
- Database: PostgreSQL
- CI/CD: GitHub Actions
- Контейнеризация: Docker
- Язык программирования: Python 3

## Как развернуть репозиторий на сервере

1. Клонируйте репозиторий
```bash
git clone https://github.com/Pr1ority/recept_blog.git
```
2. Перейдите в корневую директорию
```bash
cd foodgram
```
3. Настройте виртуальное окружение
```bash
python -m venv venv
```
Для macOS/Linux
```bash
source venv/bin/activate
```
Для Windows
```bash
source venv/Scripts/activate
```
4. Заполните .env
Пример:
```example.env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
```
5. Поднимите контейнеры в Докере
Находясь в папке infra, выполните команду
```bash
docker-compose -f docker-compose.production.yml up -d
```
6. Подготовьте базу данных
```bash
docker-compose exec backend python manage.py migrate
```
```bash
docker-compose exec backend python manage.py createsuperuser
```
```bash
docker-compose exec backend python manage.py import_ingredients
```
7. Соберите статику
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```
8. Запустите сервер
```bash
docker-compose exec backend python manage.py runserver 0.0.0.0:8000
```
## Как развернуть репозиторий локально
1. Клонируйте репозиторий
```bash
git clone https://github.com/Pr1ority/foodgram.git
```
2. Перейдите в корневую директорию
```bash
cd foodgram
```
3. Настройте виртуальное окружение
```bash
python -m venv venv
```
Для macOS/Linux
```bash
source venv/bin/activate
```
Для Windows
```bash
source venv/Scripts/activate
```
```bash
pip install -r requirements.txt
```
4. Заполните .env
Пример:
```example.env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
```
5. Подготовьте базу данных

```bash
python manage.py migrate
```
```bash
python manage.py createsuperuser
```
6. Импортируйте фикстуры
```bash
python manage.py loaddata import_ingredients
```
7. Запустите сервер
```bash
python manage.py runserver
```
8. [Спецификация API](http://localhost/api/docs/redoc.html)
