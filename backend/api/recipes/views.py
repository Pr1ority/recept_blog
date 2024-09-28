from api.filters import RecipeFilter
from api.paginations import FoodgramPageNumberPagination
from api.permissions import IsAuthorOrReadOnlyPermission
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = FoodgramPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        authors = user.follower.values_list('author', flat=True)
        recipes = Recipe.objects.filter(author__in=authors)
        page = self.paginate_queryset(recipes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite, created = Favorite.objects.get_or_create(user=user,
                                                           recipe=recipe)
        if created:
            return Response({'status': 'рецепт добавлен в избранное'},
                            status=status.HTTP_201_CREATED)
        return Response({'status': 'рецепт уже в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def unfavorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response({'status': 'рецепт удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'рецепт не находится в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipes = [item.recipe for item in shopping_cart]
        page = self.paginate_queryset(recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_in_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        cart_item, created = ShoppingCart.objects.get_or_create(user=user,
                                                                recipe=recipe)
        if created:
            return Response({'status': 'рецепт добавлен в список покупок'},
                            status=status.HTTP_201_CREATED)
        return Response({'status': 'рецепт уже в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_from_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if cart_item.exists():
            cart_item.delete()
            return Response({'status': 'рецепт удален из списка покупок'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'рецепт не в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart.exists():
            return Response({'detail': 'Ваш список покупок пуст'},
                            status=status.HTTP_400_BAD_REQUEST)
        ingredients = {}
        for item in shopping_cart:
            recipe = item.recipe
            for ingredient in recipe.ingredients.all():
                amount = RecipeIngredient.objects.get(
                    recipe=recipe, ingredient=ingredient).amount
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]['amount'] += amount
                else:
                    ingredients[ingredient.name] = {
                        'measurement_unit': ingredient.measurement_unit,
                        'amount': amount
                    }
        shopping_list = [
            f"{ingredient} — {data['amount']} {data['measurement_unit']}"
            for ingredient, data in ingredients.items()
        ]
        content = '\n'.join(shopping_list)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response
        

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name']
    ordering_fields = ['name']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission,)
