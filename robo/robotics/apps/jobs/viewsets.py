import functools

from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core import mixins as core_mixins
from users.viewsets import UserSubViewSetMixin
from tasks.viewsets import (
    TaskSubViewSetMixin, task_brief_creator_permission_required
)
from orgs.models import Organization
from .models import Job, Application
from . import serializers as job_serializers
from . import permissions as job_permissions



class TaskJobViewSet(TaskSubViewSetMixin,
                     mixins.CreateModelMixin,
                     GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = job_serializers.JobSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs.update({'exclude_fields': ('task',)})
        return super(TaskJobViewSet, self).get_serializer(*args, **kwargs)

    @task_brief_creator_permission_required
    def create(self, request, *args, **kwargs):
        if Job.objects.filter(task=self.get_task()).count():
            raise ValidationError('A job has been already created for this task')
        return super(TaskJobViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(task=self.get_task())


class JobViewSet(core_mixins.SecuredFieldMixin,
                 core_mixins.MultiSerializerViewSetMixin,
                 core_mixins.MultiSerializerCreateModelMixin,
                 core_mixins.MultiSerializerUpdateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    serializer_class = job_serializers.JobSerializer
    serializer_action_classes = {
        'create': job_serializers.JobFullCreateSerializer
    }
    permission_classes = (
        permissions.IsAuthenticated,
        job_permissions.IsCreatorOrReadOnly
    )
    secured_fields = ('organization',)

    def get_secured_field_queryset(self, field):
        if field == 'organization':
            return Organization.objects.has_member(self.request.user)
        return None

    def get_queryset(self):
        queryset = Job.objects.published()
        if self.action != 'list':
            queryset = queryset | Job.objects.created_by(self.request.user)
            return queryset.prefetch_task_fields()
        #return queryset.prefetch_task_fields()
    # here is a bug, when you pull all the jobs that you created and the jobs that
    # is internal and needs to be filtered. Figure it out.
        if not self.request.user.organizationuser_set.all():
            #return queryset.prefetch_task_fields()
            return  [item for item in queryset.prefetch_task_fields() if item.can_view == 2]
        # return queryset.prefetch_task_fields()
        #this here is also dirty code, what if people have multiple organizations?
        return [item for item in queryset.prefetch_task_fields() if item.can_view == 2 or  self.request.user.organizationuser_set.first().organization == item.creator().organizationuser_set.first().organization]

    def perform_create(self, serializer):
        return serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        job = serializer.instance
        if job.is_published():
            published_serializer = job_serializers.PublishedJobSerializer(
                job, self.request.data
            )
            published_serializer.is_valid(raise_exception=True)
        serializer.save()


class JobSubViewSetMixin(object):
    def get_job(self):
        job_pk = self.kwargs.get('job_pk', self.kwargs.get('pk'))
        job = get_object_or_404(Job, pk=job_pk)
        return job


def job_permission_required(func):
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):
        job = self.get_job()
        if not job_permissions.IsCreator().has_object_permission(self.request, self, job):
            raise PermissionDenied
        return func.__get__(self, type(self))(*args, **kwargs)
    return wrapped_func


class JobApplicationViewSet(JobSubViewSetMixin,
                            core_mixins.MultiSerializerViewSetMixin,
                            core_mixins.MultiSerializerCreateModelMixin,
                            core_mixins.MultiSerializerUpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
        job_permissions.IsApplicantOrJobCreator,
        job_permissions.IsJobCreatorOrReadOnly
    )
    serializer_action_classes = {
        'write': job_serializers.ApplicationWriteSerializer,
        'read': job_serializers.ApplicationReadSerializer,
    }

    def get_queryset(self):
        return Application.objects.filter(job=self.get_job())

    @job_permission_required
    def list(self, request, *args, **kwargs):
        # Just to add permission check
        return super(JobApplicationViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        job = self.get_job()
        if job.applied_by(self.request.user):
            return Response({'detail': 'You have already applied for this job.'},
                            status=HTTP_400_BAD_REQUEST)
        return super(JobApplicationViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(job=self.get_job(), applicant=self.request.user)


class UserJobViewSet(UserSubViewSetMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = job_serializers.JobSerializer

    def get_queryset(self):
        return Job.objects.created_by(self.get_user())


class UserApplicationViewSet(UserSubViewSetMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    serializer_class = job_serializers.ApplicationReadSerializer
    filter_fields = ('job',)

    def get_queryset(self):
        return Application.objects.filter(applicant=self.get_user())
