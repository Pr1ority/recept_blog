from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, IngredientViewSet, TagViewSet

v1_router = DefaultRouter()
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]