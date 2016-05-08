from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, org):
        return request.user == org.owner()


class IsMember(permissions.BasePermission):
    def has_object_permission(self, request, view, org):
        return org.has_member(request.user)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, org):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == org.owner()
