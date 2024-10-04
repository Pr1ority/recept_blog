from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag, Follow)

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',
                                                     'first_name', 'last_name')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_id = request.user.id
            return Follow.objects.filter(author=author.id,
                                         user=user_id).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', )

    def to_representation(self, instance):
        ingredient = instance.ingredient
        representation = {
            'id': ingredient.id,
            'name': ingredient.name,
            'measurement_unit': ingredient.measurement_unit,
            'amount': instance.amount,
        }
        return representation


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit',)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time', 'pub_date',
        )

    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient['id'],
            amount=ingredient['amount'])
            for ingredient in ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data.pop('author', None)
        self._validate_tags_and_ingredients(tags, ingredients)
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        self._validate_tags_and_ingredients(tags_data, ingredients_data)
        if ingredients_data:
            instance.ingredients.clear()

        self.tags_and_ingredients_set(instance,
                                      tags_data or instance.tags.all(),
                                      ingredients_data)
        return super().update(instance, validated_data)

    def validate_unique_items(self, items, error_message):
        unique_items = set(items)
        if len(unique_items) != len(items):
            raise ValidationError(error_message)

    def _validate_tags_and_ingredients(self, tags, ingredients):
        """Проверка на уникальность тегов и ингредиентов."""
        if tags:
            self.validate_unique_items(tags, 'Теги не должны повторяться.')
        if ingredients:
            self.validate_unique_items(
                [ingredient['id'] for ingredient in ingredients],
                'Ингредиенты не должны повторяться.'
            )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, recipe):
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user.id, recipe=recipe.id).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user.id, recipe=recipe.id).exists())


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('recipes', 'recipes_count', 'email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_recipes(self, author):

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        try:
            limit = int(limit)
            if limit < 0:
                raise ValidationError(
                    'Параметр "recipes_limit" должен быть положительным'
                    'числом или равным нулю.')
        except ValueError:
            raise ValidationError(
                'Параметр "recipes_limit" должен быть целым числом.')

        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(author):

        return author.recipes.count()

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_id = request.user.id
            return Follow.objects.filter(author=author.id,
                                         user=user_id).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar', )
