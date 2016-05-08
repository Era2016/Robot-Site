from rest_framework import permissions


class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, user):
        return user == request.user


class IsUserOrReadOnly(IsUser):
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsUserOrReadOnly, self).has_object_permission(request, view, user)
