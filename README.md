## Описание проекта

Foodgram - это сайт, на котором пользователи могут публиковать свои рецепты, добавлять рецепты других пользователей в избранное и подписываться  на пользователей.

## Автор

Бондаренко Алексей Олегович, telegram: @alovsemprivet

## Технологический стек

- Django
- Docker
- PostgreSQL
- Nginx
- GitHub Actions
- Python
- Gunicorn

## Как развернуть репозиторий на сервере

1. Клонируйте репозиторий
```bash
git clone https://github.com/Pr1ority/kittygram_final.git
```
2. Перейдите в корневую директорию
```bash
cd foodgram
```
3. Настройте виртуальное окружение
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
4. Заполните .env
Пример:
```example.env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
SECRET_KEY=your_secret_key
```
5. Поднимите контейнеры в Докере
Находясь в папке infra, выполните команду
```bash
docker-compose up
```
6. Подготовьте базу данных
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
```bash
python manage.py createsuperuser
```
```bash
python manage.py loaddata data.json
```
7. Соберите статику
```bash
python manage.py collectstatic
```
8. Запустите сервер
```bash
python manage.py runserver
```
## Как развернуть репозиторий локально
1. Клонируйте репозиторий
```bash
git clone https://github.com/Pr1ority/kittygram_final.git
```
2. Перейдите в корневую директорию
```bash
cd foodgram
```
3. Настройте виртуальное окружение
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
4. Заполните .env
Пример:
```example.env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
SECRET_KEY=your_secret_key
```
5. Подготовьте базу данных
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
```bash
python manage.py createsuperuser
```
6. Импортируйте фикстуры
```bash
python manage.py loaddata data.json
```
7. Запустите сервер
```bash
python manage.py runserver
```
8. [Спецификация API](http://localhost/api/docs/)
