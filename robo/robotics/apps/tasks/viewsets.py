import functools

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_condition import Or, And

from core import mixins as core_mixins
from core import permissions as core_permissions
from common import enums
from users import viewsets as user_viewsets
from comments.serializers import CommentSerializer
from orgs import viewsets as org_viewsets
from orgs.models import Organization
from .models import TaskBrief, Task
from .serializers import (
    TaskBriefSerializer, PublishedTaskBriefSerializer,
    TaskSerializer, PublishedTaskSerializer
)
from . import permissions as task_permissions
from .pagination import NotificationPagination


class TaskBriefViewSet(core_mixins.SecuredFieldMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = TaskBriefSerializer
    permission_classes = (
        Or(task_permissions.IsCreator,
           And(Or(task_permissions.IsOneOfAssignees,
                  task_permissions.IsInOrganization),
               core_permissions.ReadOnly)),
    )
    secured_fields = ['organization']

    def get_secured_field_queryset(self, field):
        if field == 'organization':
            return Organization.objects.has_member(self.request.user)
        return None

    def get_queryset(self):
        return (TaskBrief.objects.published() |
                TaskBrief.objects.created_by(self.request.user))

    def perform_create(self, serializer):
        return serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        task_brief = serializer.instance
        if task_brief.published:
            published_serializer = PublishedTaskBriefSerializer(
                task_brief, self.request.data
            )
            published_serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer.save()
            if (serializer.validated_data.get('published', False)):
                published_serializer = PublishedTaskBriefSerializer(
                    task_brief, {'published': True}
                )
                published_serializer.is_valid(raise_exception=True)
                published_serializer.save()


class TaskBriefSubViewSetMixin(object):
    def get_brief(self):
        brief_pk = self.kwargs.get('brief_pk', self.kwargs.get('pk'))
        brief = get_object_or_404(TaskBrief, pk=brief_pk)
        return brief


def brief_permission_required(permission_classes):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            brief = self.get_brief()
            for permission_cls in permission_classes:
                if not permission_cls().has_object_permission(self.request, self, brief):
                    raise PermissionDenied
            return func.__get__(self, type(self))(*args, **kwargs)
        return wrapped_func
    return wrapper


def brief_creator_permission_required(func):
    return brief_permission_required((task_permissions.IsCreator,))(func)


def brief_general_permissions_required(func):
    return brief_permission_required(
        (Or(task_permissions.IsOneOfAssignees, task_permissions.IsInOrganization),)
    )(func)


def published_brief_required(func):
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):
        brief = self.get_brief()
        if not brief.published:
            raise NotFound
        return func.__get__(self, type(self))(*args, **kwargs)
    return wrapped_func


class TaskBriefCommentViewSet(TaskBriefSubViewSetMixin,
                              mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return self.get_brief().comments.all()

    @published_brief_required
    @brief_general_permissions_required
    def create(self, request, *args, **kwargs):
        # Just to add permission check
        return super(TaskBriefCommentViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, content_object=self.get_brief())

    @published_brief_required
    @brief_general_permissions_required
    def list(self, request, *args, **kwargs):
        # Just to add permission check
        return super(TaskBriefCommentViewSet, self).list(request, *args, **kwargs)


class BriefTaskViewSet(TaskBriefSubViewSetMixin,
                       core_mixins.SecuredFieldMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = TaskSerializer
    permission_classes = (
        Or(
            Or(task_permissions.IsBriefCreator, task_permissions.IsAssignee),
            core_permissions.ReadOnly
        ),
    )
    pagination_class = NotificationPagination
    secured_fields = ['predecessor', 'successor', 'assignee']

    def get_queryset(self):
        return self.get_brief().task_set

    def get_secured_field_queryset(self, field):
        brief = self.get_brief()
        if field in ['predecessor', 'successor']:
            return brief.tasks()
        elif field == 'assignee':
            if brief.organization:
                return brief.organization.members()
            return Organization.objects.none()
        return None

    def get_serializer(self, *args, **kwargs):
        kwargs.update({'exclude_fields': ('task_brief',)})
        return super(BriefTaskViewSet, self).get_serializer(*args, **kwargs)

    @brief_general_permissions_required
    def list(self, request, *args, **kwargs):
        ordered_tasks = self.get_brief().ordered_tasks()
        serializer = self.get_serializer(ordered_tasks, many=True)
        return self.get_paginated_response(serializer.data)

    @brief_creator_permission_required
    def create(self, request, *args, **kwargs):
        if self.get_brief().published:
            return Response({'detail': 'You cannot create task for published brief'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super(BriefTaskViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(
            task_brief=self.get_brief(), assigner=self.request.user
        )

    @brief_general_permissions_required
    def retrieve(self, request, *args, **kwargs):
        # Just to add permission check
        return super(BriefTaskViewSet, self).retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        task = serializer.instance
        if task.task_brief.published:
            published_serializer = PublishedTaskSerializer(task, self.request.data)
            published_serializer.is_valid(raise_exception=True)
        serializer.save(assigner=self.request.user)

    @brief_creator_permission_required
    def destroy(self, request, *args, **kwargs):
        if self.get_brief().published:
            return Response({'detail': 'You cannot delete task for published brief'},
                            status=status.HTTP_400_BAD_REQUEST)
        task = self.get_object()
        if task.type == enums.TaskType.ACCEPT:
            return Response({'detail': 'Accept task cannot be deleted'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super(BriefTaskViewSet, self).destroy(request, *args, **kwargs)


class TaskSubViewSetMixin(object):
    def get_task(self):
        task_pk = self.kwargs.get('task_pk', self.kwargs.get('pk'))
        task = get_object_or_404(Task, pk=task_pk)
        return task


def task_permission_required(permission_classes):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            task = self.get_task()
            for permission_cls in permission_classes:
                if not permission_cls().has_object_permission(self.request, self, task):
                    raise PermissionDenied
            return func.__get__(self, type(self))(*args, **kwargs)
        return wrapped_func
    return wrapper


def task_brief_creator_permission_required(func):
    return task_permission_required((task_permissions.IsBriefCreator,))


class UserTaskBriefViewSet(user_viewsets.UserSubViewSetMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = TaskBriefSerializer

    def get_queryset(self):
        return (TaskBrief.objects.created_by(self.get_user())
                                 .prefetch_common_fields(exclude=('article',))
                                 .annotate_task_stats()
                                 .order_by('deadline'))

    def get_serializer(self, *args, **kwargs):
        kwargs.update({
            'exclude_fields': ('article', 'current_assignee')
        })
        return super(UserTaskBriefViewSet, self).get_serializer(*args, **kwargs)


class UserTaskViewSet(user_viewsets.UserSubViewSetMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = TaskSerializer
    filter_fields = ('status',)

    def get_queryset(self):
        return (Task.objects.published()
                            .assigned_to(self.get_user())
                            .prefetch_common_fields(exclude=('job',))
                            .prefetch_task_brief_fields())

    def get_serializer(self, *args, **kwargs):
        kwargs.update({'exclude_fields': ('job',)})
        return super(UserTaskViewSet, self).get_serializer(*args, **kwargs)


class OrganizationTaskBriefViewSet(org_viewsets.OrganizationSubViewSetMixin,
                                   mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    serializer_class = TaskBriefSerializer

    def get_queryset(self):
        return (TaskBrief.objects.published()
                                 .in_organization(self.get_organization())
                                 .prefetch_common_fields(exclude=('article',))
                                 .annotate_task_stats())

    def get_serializer(self, *args, **kwargs):
        kwargs.update({
            'exclude_fields': ('organization', 'article', 'current_assignee')
        })
        return super(OrganizationTaskBriefViewSet, self).get_serializer(*args, **kwargs)

    @org_viewsets.organization_member_permission_required
    def list(self, request, *args, **kwargs):
        # just to add permission check
        return super(OrganizationTaskBriefViewSet, self).list(request, *args, **kwargs)


class OrganizationTaskViewSet(org_viewsets.OrganizationSubViewSetMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    serializer_class = TaskSerializer
    filter_fields = ('status',)

    def get_queryset(self):
        return (Task.objects.published()
                            .in_organization(self.get_organization())
                            .prefetch_common_fields(exclude=('job',))
                            .prefetch_task_brief_fields()
                            .order_by('deadline'))

    def get_serializer(self, *args, **kwargs):
        kwargs.update({'exclude_fields': ('job',)})
        return super(OrganizationTaskViewSet, self).get_serializer(*args, **kwargs)

    @org_viewsets.organization_member_permission_required
    def list(self, request, *args, **kwargs):
        # just to add permission check
        return super(OrganizationTaskViewSet, self).list(request, *args, **kwargs)
