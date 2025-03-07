from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import (Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Favorite, Follow, Tag)


User = get_user_model()


class RecipeIngredientInlineForm(forms.ModelForm):
    class Meta:
        model = Recipe.ingredients.through
        fields = ['ingredient', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.all()
        self.fields['ingredient'].label_from_instance = (
            lambda ingredient: (f'{ingredient.name}'
                                f'({ingredient.measurement_unit})')
        )


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1
    form = RecipeIngredientInlineForm


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'formatted_pub_date', 'favorite_count',
                    'id',
                    'cooking_time', 'tags_list', 'ingredients_list',
                    'image_display')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags', 'author')
    inlines = [RecipeIngredientInline]

    @admin.display(description='в избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Дата публикации')
    def formatted_pub_date(self, recipe):
        return recipe.pub_date.strftime('%d %b %y')

    @admin.display(description='Теги')
    @mark_safe
    def tags_list(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_list(self, recipe):
        return '<br>'.join(
            f'{recipe_ingredient.ingredient.name} '
            f'({recipe_ingredient.ingredient.measurement_unit}) — '
            f'{recipe_ingredient.amount}'
            for recipe_ingredient
            in recipe.recipe_ingredients.select_related('ingredient')
        )

    @admin.display(description='Изображение')
    @mark_safe
    def image_display(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.image.url}" width="100" height="100" />'
        return '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'id', 'first_name', 'last_name',
                    'follows_count', 'followers_count',
                    'recipes_count', 'avatar_display')
    search_fields = ('email', 'username')

    @admin.display(description='подписок')
    def follows_count(self, user):
        return user.authors.count()

    @admin.display(description='подписчиков')
    def followers_count(self, user):
        return user.followers.count()

    @admin.display(description='рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_display(self, user):
        if user.avatar:
            return f'<img src="{user.avatar.url}" width="100" height="100" />'
        return '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


admin.site.unregister(Group)
