from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowViewSet

v1_router = DefaultRouter()
v1_router.register(r'follow', FollowViewSet, basename='follow')
v1_router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path('', include(v1_router.urls)),
]
