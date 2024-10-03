import json
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тегов из файла JSON'

    def handle(self, *args, **kwargs):
        with open('data/tags.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Tag.objects.get_or_create(
                    name=item['name'],
                    slug=item['slug']
                )
        self.stdout.write(self.style.SUCCESS('Теги успешно импортированы'))
