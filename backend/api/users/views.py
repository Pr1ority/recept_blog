from rest_framework import filters, permissions, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import FollowSerializer, UserSerializer

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
