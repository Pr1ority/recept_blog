from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'follow', FollowViewSet, basename='follow')
v1_router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(v1_router.urls)),
]
