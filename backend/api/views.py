from api.filters import RecipeFilter
from api.paginations import FoodgramPageNumberPagination
from api.permissions import IsAuthorOrReadOnlyPermission
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import FileResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag, Follow)
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer,
                          FollowSerializer, AvatarSerializer)
from .utils import render_shopping_list

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = FoodgramPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        """
        Переопределяем get_queryset, чтобы корректно фильтровать рецепты
        по корзине покупок пользователя.
        """
        queryset = super().get_queryset()
        user = self.request.user

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(shoppingcarts__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def update_user_recipe_status(request, model, recipe, user,
                                  success_add_message, success_remove_message):

        if request.method == 'POST':
            _, created = model.objects.get_or_create(recipe=recipe,
                                                     user=user)
            if not created:
                raise ValidationError(
                    {'status': f'рецепт уже {success_add_message}'})
            return Response(
                {'status': f'рецепт добавлен {success_add_message}'},
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(model, user=user.id, recipe=recipe.id).delete()
            return Response(
                {'status': f'рецепт удален {success_remove_message}'},
                status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        return self.update_user_recipe_status(
            request=request,
            model=Favorite,
            recipe=recipe,
            user=user,
            success_add_message='в избранное',
            success_remove_message='из избранного'
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        return self.update_user_recipe_status(
            request=request,
            model=ShoppingCart,
            recipe=recipe,
            user=user,
            success_add_message='в список покупок',
            success_remove_message='из списка покупок'
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart.exists():
            raise ValidationError({'status': 'Ваш список покупок пуст'})

        ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart.values_list('recipe', flat=True)).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(total_amount=Sum('amount')
                                                     )

        recipes = Recipe.objects.filter(
            id__in=shopping_cart.values_list('recipe', flat=True))
        return FileResponse(render_shopping_list(ingredients, recipes),
                            content_type='text/plain',
                            filename='shopping_list.txt')

    @action(
        detail=True,
        methods=('get', ),
        url_path='get-link',
        url_name='get-link',
    )
    def get_recipe_short_link(self, request, pk=None):
        if not Recipe.objects.filter(id=pk).exists():
            raise ValidationError(
                {'status':
                 f'Рецепт с ID {pk} не найден'})
        short_link = f'{request.build_absolute_uri("/")[:-1]}/r/{str(pk)}/'
        return JsonResponse({'short-link': short_link})


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission,)


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):

        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, id):

        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            _, created = Follow.objects.get_or_create(author=author,
                                                      user=user)
            if user == author:
                raise ValidationError(
                    {'status': 'нельзя подписаться на самого себя'})
            if created:
                raise ValidationError(
                    {'status': f'вы уже подписаны на {author.username}'})
            return Response(
                {'message': f'вы подписались на {author.username}'},
                status=status.HTTP_201_CREATED)

        get_object_or_404(Follow, user=user.id, author=author.id).delete()
        return Response({'message': f'вы отписались от {author.username}'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated, ),
    )
    def subscriptions(self, request):

        queryset = User.objects.filter(authors__user=self.request.user)
        if not queryset:
            raise ValidationError({'status': 'у вас нет подписок'})

        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def update_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise ValidationError({'status': 'не удалось обновить аватар'})

        user.avatar.delete()
        user.save()
        return Response({'detail': 'Аватар успешно удален'},
                        status=status.HTTP_204_NO_CONTENT)
