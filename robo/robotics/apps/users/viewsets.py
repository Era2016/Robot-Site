from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404

from rest_framework import mixins, permissions, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import detail_route, list_route

from common import enums
from . import serializers as user_serializers
from . import permissions as user_permissions
from .pagination import NotificationPagination
from .filters import NotificationFilter

# Custom user model
User = get_user_model()


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.filter(
        is_staff=False, is_superuser=False
    )
    serializer_class = user_serializers.UserSerializer
    permission_classes = (
        permissions.IsAuthenticated, user_permissions.IsUserOrReadOnly
    )

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            queryset = queryset.filter(userrole__role=enums.UserRole.WRITER)
        return (queryset.prefetch_related('userprofile', 'articles__keywords')
                        .annotate(_rating=Avg('taskassignees__task__ratings__overall_rating'))
                        .annotate(_rating__count=Count('taskassignees__task__ratings')))

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            kwargs.update(
                {'fields': ('id', 'username', 'first_name', 'last_name',
                            'keywords', 'picture', 'description',
                            'rating', 'rating_count')}
            )
        else:
            user_pk = self.kwargs.pop('pk', None)
            if self.request.user.pk != int(user_pk):
                kwargs.update({'exclude_fields': ('email',)})
        return super(UserViewSet, self).get_serializer(*args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        user_serializer = self.get_serializer(
            user, data=request.data, partial=partial
        )
        user_profile_serializer = user_serializers.UserProfileSerializer(
            user.userprofile, data=request.data, partial=partial
        )
        if user_serializer.is_valid() and user_profile_serializer.is_valid():
            user_serializer.save()
            user_profile_serializer.save()
            return Response(user_serializer.data)

        errors = {}
        errors.update(user_serializer.errors)
        errors.update(user_profile_serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @detail_route(methods=['post'], url_path='set-picture')
    def update_profile_picture(self, request, *arg, **kwargs):
        user = self.get_object()
        picture_serializer = user_serializers.UserPictureSerializer(
            user.userprofile, data=request.data
        )
        picture_serializer.is_valid(raise_exception=True)
        picture_serializer.save()
        return Response(picture_serializer.data)


class UserSubViewSetMixin(object):
    user_permission_exempt_actions = None

    def check_permissions(self, request):
        if (not self.user_permission_exempt_actions or
                self.action not in self.user_permission_exempt_actions):
            self.get_user(require_permission=True)
        return super(UserSubViewSetMixin, self).check_permissions(request)

    def get_user(self, require_permission=False):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        if (require_permission):
            has_permission = user_permissions.IsUser().has_object_permission(
                self.request, self, user
            )
            if not has_permission:
                raise PermissionDenied
        return user


class UserNotificationViewSet(UserSubViewSetMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    serializer_class = user_serializers.NotificationSerializer
    permission_classes = (user_permissions.IsUser,)
    pagination_class = NotificationPagination
    filter_class = NotificationFilter

    def get_queryset(self):
        return self.get_user().notifications.all().prefetch_related(
            'actor', 'action_object', 'target'
        )

    @list_route(methods=['POST'], url_path='mark-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        self.get_user().notifications.mark_all_as_read()
        return Response({'status': 'success'})
