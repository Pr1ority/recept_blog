from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in
            permissions.SAFE_METHODS and obj.author == request.user)
