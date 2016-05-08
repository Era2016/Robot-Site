import functools

from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import JSONRenderer

from users.viewsets import UserSubViewSetMixin
from .models import Organization, OrganizationUser
from . import serializers as org_serializers
from . import permissions as org_permissions
from users.serializers import UserSerializer

class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = org_serializers.OrganizationSerializer
    permission_classes = (
        permissions.IsAuthenticated, org_permissions.IsOwnerOrReadOnly
    )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @detail_route(methods=['post'], url_path='set-picture')
    def update_profile_picture(self, request, *arg, **kwargs):
        organization = self.get_object()
        picture_serializer = org_serializers.OrganizationPictureSerializer(
            organization, data=request.data
        )
        picture_serializer.is_valid(raise_exception=True)
        picture_serializer.save()
        return Response(picture_serializer.data)

    @detail_route(methods=['get'], url_path='employee')
    def get_employee(self, request, *arg, **kwargs):
        organization = self.get_object()
        user_serializer = UserSerializer(organization.members(), many=True)
        return Response(user_serializer.data)


class UserOrganizationViewSet(UserSubViewSetMixin,
                              ListModelMixin,
                              GenericViewSet):
    serializer_class = org_serializers.OrganizationSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs.update({'fields': ('id', 'name')})
        return super(UserOrganizationViewSet, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        return Organization.objects.owned_by(self.get_user())


class OrganizationUserViewSet(ModelViewSet,
                              ListModelMixin,
                              GenericViewSet):
    queryset = OrganizationUser.objects.all()
    serializer_class = org_serializers.OrganizationUserSerializer

    '''
    def get_serializer(self, *args, **kwargs):
        kwargs.update({'fields': ('id', 'user', 'organization')})
        return super(OrganizationUserViewSet, self).get_serializer(*args, **kwargs)

    '''
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return OrganizationUser.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)





class OrganizationSubViewSetMixin(object):
    def get_organization(self):
        organization_pk = self.kwargs.get('org_pk', self.kwargs.get('pk'))
        organization = get_object_or_404(Organization, pk=organization_pk)
        return organization


def organization_owner_permission_required(func):
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):
        organization = self.get_organization()
        if not org_permissions.IsOwner().has_object_permission(
            self.request, self, organization
        ):
            raise PermissionDenied
        return func.__get__(self, type(self))(*args, **kwargs)
    return wrapped_func


def organization_member_permission_required(func):
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):
        organization = self.get_organization()
        if not org_permissions.IsMember().has_object_permission(
            self.request, self, organization
        ):
            raise PermissionDenied
        return func.__get__(self, type(self))(*args, **kwargs)
    return wrapped_func
