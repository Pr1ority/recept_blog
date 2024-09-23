from django.contrib.auth import get_user_model
from djoser.serializers import (UserSerializer as BaseUserSerializer,
                                UserCreateSerializer)
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    following = serializers.SlugRelatedField(slug_field='username',
                                             queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following')

    def validate_following(self, author):
        user = self.context['request'].user
        if user == author:
            raise serializers.ValidationError('Вы не можете отслеживать себя')
        if Follow.objects.filter(user=user, following=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя')
        return author


class UserCreateSerializer(UserCreateSerializer):
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


class UserSerializer(BaseUserSerializer):
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

    def get_is_subscribed(self, obj):
        user_id = self.context.get('request').user.id
        return Follow.objects.filter(
            author=obj.id, user=user_id
        ).exists()
