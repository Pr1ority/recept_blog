from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Имя')
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
