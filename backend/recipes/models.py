from django.db import models
from django.contrib.auth import get_user_model

from tags.models import Tag

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    measurement_unit = models.CharField(max_length=50, verbose_name='Единица измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ингредиет'
        verbose_name_plural = 'Ингредиенты' 

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/images/', verbose_name='Изображение')
    text = models.TextField('Текст')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(help_text='Время в минутах', verbose_name='Время приготовления')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты' 


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Количество')

    def __str__(self):
        return f'{self.amount} {self.ingredient.name} для {self.recipe.title}'
    
    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта' 


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites', verbose_name='Пользователь')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               related_name='favorites', verbose_name='Рецепт')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.title} в избранное'
    
    class Meta:
        verbose_name = 'избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart', verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_shopping_cart', verbose_name='Рецепт')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.title} в список покупок'
    
    class Meta:
        verbose_name = 'список покупок'
