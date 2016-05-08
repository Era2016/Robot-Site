from rest_framework import permissions


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, task_brief):
        return request.user == task_brief.creator


class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, task_brief):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == task_brief.creator


class IsOneOfAssignees(permissions.BasePermission):
    def has_object_permission(self, request, view, task_brief):
        return task_brief.has_assignee(request.user)


class IsCurrentAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, task_brief):
        return request.user == task_brief.current_assignee()


class IsInOrganization(permissions.BasePermission):
    def has_object_permission(self, request, view, task_brief):
        return bool(task_brief.organization and
                    task_brief.organization.has_member(request.user))


class IsBriefCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, task):
        return IsCreator().has_object_permission(request, view, task.task_brief)


class IsAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, task):
        return request.user == task.assignee()


class IsOneOfBriefAssignees(permissions.BasePermission):
    def has_object_permission(self, request, view, task):
        return task.task_brief.has_assignee(request.user)
