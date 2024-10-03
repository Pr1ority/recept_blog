from django.db import models
from django.contrib.auth import get_user_model

from .utils import UserRecipeBase
from .validators import validate_cooking_time, validate_ingredients


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True,
                            verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг', max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name='Имя')
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение')
    text = models.TextField('Текст')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Продукты')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        help_text='Время в минутах', verbose_name='Время приготовления',
        validators=validate_cooking_time)
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Продукт',
                                   related_name='in_recipe')
    amount = models.PositiveIntegerField('Количество',
                                         validators=validate_ingredients)

    def __str__(self):
        return f'{self.amount} {self.ingredient.name} для {self.recipe.name}'

    class Meta:
        verbose_name = 'продукт рецепта'
        verbose_name_plural = 'Продукты рецепта'


class Favorite(UserRecipeBase):

    class Meta:
        verbose_name = 'избранное'


class ShoppingCart(UserRecipeBase):

    class Meta:
        verbose_name = 'список покупок'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='followings',
                               verbose_name='Авторы')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
