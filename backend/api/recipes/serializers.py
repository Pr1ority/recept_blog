import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers

from api.users.serializers import UserSerializer

User = get_user_model()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def to_representation(self, instance):
        print(f"Ingredient instance in to_representation: {instance}")
        representation = super().to_representation(instance)
        representation['name'] = instance.ingredient.name
        representation['measurement_unit'] = instance.ingredient.measurement_unit
        return representation


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"

            data = ContentFile(base64.b64decode(imgstr), name=file_name)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


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


class RecipeCreateSerializer(serializers.ModelSerializer):
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
        print(f"Ингредиенты в tags_and_ingredients_set: {ingredients}")
        recipe_ingredients = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(pk=ingredient['id']),
            amount=ingredient['amount'] 
        ) for ingredient in ingredients
        ]
        for ri in recipe_ingredients:
            print(f"RecipeIngredient: {ri}")
        
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        print(f"Создан рецепт: {recipe}, с ингредиентами: {recipe.ingredients_list.all()}")
        return recipe


    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()

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

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(user=user_id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = '__all__'



class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeCreateSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe, context=self.context).data
