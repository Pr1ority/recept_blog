import json
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из файла JSON'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            Ingredient.objects.bulk_create(Ingredient(**item)
                                           for item in data)
        self.stdout.write(self.style.SUCCESS(
            'Ингредиенты успешно импортированы'))
