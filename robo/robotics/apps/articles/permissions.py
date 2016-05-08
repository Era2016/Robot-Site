from rest_framework import permissions

from tasks import permissions as task_permissions


class IsOneOfBriefAssignees(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        return task_permissions.IsOneOfAssignees().has_object_permission(
            request, view, article.task_brief
        )


class IsInBriefOrganization(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        return task_permissions.IsInOrganization().has_object_permission(
            request, view, article.task_brief
        )


class IsBriefCurrentAssigneeOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        if request.method in permissions.SAFE_METHODS:
            return True
        return task_permissions.IsCurrentAssignee().has_object_permission(
            request, view, article.task_brief
        )


class IsUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == article.user
