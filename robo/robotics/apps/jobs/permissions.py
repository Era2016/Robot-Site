from rest_framework import permissions


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, job):
        return request.user == job.creator()


class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, job):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == job.creator()


class IsApplicantOrJobCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, application):
        return (request.user == application.applicant or
                request.user == application.job.creator())


class IsJobCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, application):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == application.job.creator()
