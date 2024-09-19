import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Recipe
        fields = ['title', 'tags', 'author']
