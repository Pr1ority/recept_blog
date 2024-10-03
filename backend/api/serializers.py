from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer)

from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag, Follow)

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_id = request.user.id
            return Follow.objects.filter(author=author.id,
                                         user=user_id).exists()
        return False


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

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
        fields = ['id', 'amount', 'name', 'measurement_unit']


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
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient['id'],
            amount=ingredient['amount'])
            for ingredient in ingredients])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data.pop('author', None)
        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise ValidationError('Теги не должны повторяться.')

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        unique_ingredient_ids = set(ingredient_ids)
        if len(unique_ingredient_ids) != len(ingredient_ids):
            raise ValidationError('Ингредиенты не должны повторяться.')

        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        unique_tags = set(tags_data)
        if len(unique_tags) != len(tags_data):
            raise ValidationError('Теги не должны повторяться.')

        ingredient_ids = [ingredient['id'] for ingredient in ingredients_data]
        unique_ingredient_ids = set(ingredient_ids)
        if len(unique_ingredient_ids) != len(ingredient_ids):
            raise ValidationError('Ингредиенты не должны повторяться.')

        instance = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.tags_and_ingredients_set(instance, ingredients_data)

        return instance


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


class RecipeForFollowSerializer(serializers.ModelSerializer):

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
        fields = ['recipes', 'recipes_count', 'email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed']

    def get_recipes(self, author):

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeForFollowSerializer(recipes, many=True).data

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
        fields = ['avatar']
