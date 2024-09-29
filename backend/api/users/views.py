from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models import Follow
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

    @action(detail=True, methods=['post'])
    def subscribe(self, request):
        author = self.get_object()
        user = request.user
        follow, created = Follow.objects.get_or_create(user=user,
                                                       author=author)
        if created:
            return Response({'status': 'оформлена подписка на автора'},
                            status=status.HTTP_201_CREATED)
        return Response({'status': 'вы уже подписаны на автора'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response({'status': 'вы отписались от автора'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'вы не подписаны на автора'},
                        status=status.HTTP_400_BAD_REQUEST)
