import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.CharFilter(field_name='author__username',
                                       lookup_expr='icontains')

    class Meta:
        model = Recipe
        fields = ['name', 'tags', 'author']
