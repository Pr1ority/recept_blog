import django_filters
from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.NumberFilter(field_name='author__id')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value:
            return recipes.filter(in_shopping_list_by__user=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ['name', 'tags', 'author']


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
