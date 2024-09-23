from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from .serializers import FollowSerializer

User = get_user_model()


class FollowViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()
