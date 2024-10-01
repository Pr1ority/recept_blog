from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from users.models import Follow
from .serializers import UserSerializer, FollowSerializer, AvatarSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny]
        elif self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
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
        subscription_exists = Follow.objects.filter(user=user.id,
                                                    author=author.id).exists()

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'message': 'нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if subscription_exists:
                return Response(
                    {'message': f'вы уже подписаны на {author.username}'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscribe = Follow.objects.create(
                user=user,
                author=author
            )
            subscribe.save()
            return Response(
                {'message': f'вы подписались на {author.username}'},
                status=status.HTTP_201_CREATED)
        if subscription_exists:
            Follow.objects.filter(user=user.id, author=author.id).delete()
            return Response({'message': f'вы отписались от {author.username}'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'message': f'вы не подписаны на {author.username}'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated, ),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):

        queryset = User.objects.filter(following__user=self.request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = FollowSerializer(pages, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('у вас нет подписок',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def update_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response({'detail': 'Аватар успешно удален'},
                            status=status.HTTP_204_NO_CONTENT)
