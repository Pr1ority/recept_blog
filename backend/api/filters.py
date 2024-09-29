import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.NumberFilter(field_name='author__id')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_list_by__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['name', 'tags', 'author']
