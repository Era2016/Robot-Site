from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response

from users.viewsets import UserSubViewSetMixin
from tasks.viewsets import (
    TaskSubViewSetMixin, task_permission_required,
    TaskBriefSubViewSetMixin, brief_permission_required
)
from tasks import permissions as task_permissions
from .models import Rating
from . import serializers as rating_serializers


class TaskRatingViewSet(TaskSubViewSetMixin,
                        mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = Rating.objects.all().prefetch_common_fields()
    serializer_class = rating_serializers.RatingSerializer

    @task_permission_required((task_permissions.IsOneOfBriefAssignees,))
    def create(self, request, *args, **kwargs):
        task = self.get_task()
        if not task.task_brief.finished():
            return Response({'detail': 'You cannot rate task in incomplete brief.'},
                            status=HTTP_400_BAD_REQUEST)
        elif self.request.user == task.assignee:
            return Response({'detail': 'You cannot rate your own task'},
                            status=HTTP_400_BAD_REQUEST)
        elif Rating.objects.filter(task=task, rater=self.request.user).count():
            return Response({'detail': 'You have already rated this task'},
                            status=HTTP_400_BAD_REQUEST)
        return super(TaskRatingViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(task=self.get_task(), rater=self.request.user)


class TaskBriefRatingViewSet(TaskBriefSubViewSetMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    serializer_class = rating_serializers.RatingSerializer
    filter_fields = ('rater',)

    def get_queryset(self):
        return Rating.objects.in_brief(self.get_brief()).prefetch_common_fields()

    @brief_permission_required((task_permissions.IsOneOfAssignees,))
    def list(self, request, *args, **kwargs):
        # Just to add permission check
        return super(TaskBriefRatingViewSet, self).list(request, *args, **kwargs)


class UserRatingViewSet(UserSubViewSetMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    serializer_class = rating_serializers.RatingSerializer
    user_permission_exempt_actions = ('list',)

    def get_queryset(self):
        return Rating.objects.has_ratee(self.get_user()).prefetch_common_fields()
