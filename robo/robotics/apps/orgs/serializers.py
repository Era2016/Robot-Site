from django.db import transaction
from rest_framework import serializers

from core import serializers as core_serializers
from .models import Organization, OrganizationUser


class OrganizationSerializer(core_serializers.DynamicFieldsModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'website','industry', 'description', 'picture',
                  'year_founded', 'size', 'owner')
        read_only_fields = ['id', 'picture']

    @transaction.atomic
    def create(self, validated_data):
        owner = validated_data.pop('owner')
        organization = super(OrganizationSerializer, self).create(validated_data)
        organization.set_owner(owner)
        return organization


class OrganizationPictureSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['picture']


class OrganizationUserSerializer(core_serializers.ModelSerializer):
    #user = serializer.(settings.AUTH_USER_MODEL)
    #organization = models.ForeignKey(Organization)
    #user = serializers.PrimaryKeyRelatedField(read_only = True)
    #organization = OrganizationSerializer(read_only = True)
    class Meta:
        model = OrganizationUser
        fields = ['id', 'user', 'organization', 'user_role']
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        # when you are using organization user to create a link, it's always gonna be an emploee.
        owner = validated_data.pop('owner') # just in case that you will need to use owner some time.
        organization_user = super(OrganizationUserSerializer, self).create(validated_data)
        return organization_user
