from django.urls import include, path

urlpatterns = [
    path('recipes/', include('api.recipes.urls')),
    path('users/', include('api.users.urls')),
]
