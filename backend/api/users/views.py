from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models import Follow
from recipes.models import Recipe
from .serializers import UserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny]
        elif self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if user == author:
                return Response({'error': 'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Follow.objects.filter(user=user, author=author).exists():
                return Response({'error': 'Вы уже подписаны на автора'},
                                status=status.HTTP_400_BAD_REQUEST)

            Follow.objects.create(user=user, author=author)
            return Response({'status': 'Подписка успешно оформлена'},
                            status=status.HTTP_201_CREATED)

        elif request.method == 'delete':
            follow = Follow.objects.filter(user=user, author=author)

            if not follow.exists():
                return Response({'error': 'Вы не подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST)

            follow.delete()
            return Response({'status': 'Вы отписались от автора'},
                            status=status.HTTP_204_NO_CONTENT)

        return Response({'error': 'Метод не поддерживается'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
