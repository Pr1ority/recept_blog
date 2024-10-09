from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

COOKING_TIME_MIN_VALUE = 1
AMOUNT_MIN_VALUE = 1


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Почта',
                              max_length=254)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,
                               verbose_name='Аватар')
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message=('Ник содержит недопустимые символы.'
                     ' Допустимы только буквы, цифры, и символы @/./+/-/_.'),
        )],
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя',
                                  blank=True)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия',
                                 blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class UserRecipeBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='%(class)ss')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='%(class)ss')

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='%(class)ss_recipe_unique')
        ]

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name}'


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
        help_text='Время в минутах',
        verbose_name='Время (мин)',
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN_VALUE,
                f'Время не может быть меньше {COOKING_TIME_MIN_VALUE}')])
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
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Продукт',
                                   related_name='in_recipes')
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(
            AMOUNT_MIN_VALUE,
            f'Количество продукта не может быть меньше {AMOUNT_MIN_VALUE}')])

    def __str__(self):
        return f'{self.amount} {self.ingredient.name} для {self.recipe.name}'

    class Meta:
        verbose_name = 'продукт рецепта'
        verbose_name_plural = 'Продукты рецепта'


class Favorite(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='authors',
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
