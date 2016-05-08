from rest_framework import serializers
from rest_framework.fields import empty

from . import mixins as core_mixins


class ModelSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    include_timestamp_fields = True

    def get_field_names(self, *args, **kwargs):
        # hack to add 'created' & 'modified' fields
        # http://www.django-rest-framework.org/api-guide/serializers/#customizing-the-default-fields
        field_names = super(ModelSerializer, self).get_field_names(*args, **kwargs)
        if self.include_timestamp_fields:
            timestamp_field_names = ('created', 'modified')
            if isinstance(field_names, list):
                field_names.extend(timestamp_field_names)
            else:
                field_names += timestamp_field_names
        return field_names


class DynamicFieldsModelSerializer(core_mixins.DynamicFieldsSerializerMixin, ModelSerializer):
    pass


class PrivateFieldsModelSerializer(DynamicFieldsModelSerializer):
    """
    A ModelSerializer that takes an additional `include_private` argument that
    controls whether to show declared private fields.
    """
    private_fields = None

    def __init__(self, *args, **kwargs):
        include_private = kwargs.pop('include_private', False)
        if not include_private:
            assert self.private_fields is not None, (
                "No private fields to exclude in %s" %
                self.__class__.__name__
            )

            exclude_fields = kwargs.pop('exclude_fields', ())
            exclude_fields += self.private_fields
            kwargs.update({'exclude_fields': exclude_fields})

        super(PrivateFieldsModelSerializer, self).__init__(*args, **kwargs)


class ReadOnlyModelSerializer(ModelSerializer):
    """
    A ModelSerializer that automatically flags all fields as read-only
    """

    def __init__(self, *args, **kwargs):
        super(ReadOnlyModelSerializer, self).__init__(*args, **kwargs)

        for field_name in set(self.fields.keys()):
            self.fields[field_name].read_only = True


class RequiredFieldModelSerializer(core_mixins.RequiredFieldsSerializerMixin,
                                   ModelSerializer):
    pass


class DynamicFieldsReadOnlyModelSerializer(DynamicFieldsModelSerializer):
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsReadOnlyModelSerializer, self).__init__(*args, **kwargs)

        for field_name in set(self.fields.keys()):
            self.fields[field_name].read_only = True


class InternalDataModelSerializerMixin(object):
    def __init__(self, instance, data=empty, **kwargs):
        # We also use instance's properties as data for validation to make sure
        # that at the time of publish, there's no empty required fields
        assert instance is not None, (
            'instance is required for subclass of'
            'InternalDataModelSerializerMixin - %s' %
            self.__class__.__name__
        )
        serializer_class = getattr(self.Meta, 'internal_data_serializer_class', None)
        if not serializer_class:
            model_class = getattr(self.Meta, 'model', None)
            assert model_class is not None, (
                'model class not found in %s' % self.__class__.__name__
            )
            serializer_class = create_model_serializer(model_class)
        instance_data = serializer_class(instance).data
        if data is empty:
            data = instance_data
        else:
            data = dict(list(instance_data.items()) + list(data.items()))
        super(InternalDataModelSerializerMixin, self).__init__(instance, data, **kwargs)


def create_model_serializer(modelClass):
    class DynamicModelSerializer(ModelSerializer):
        class Meta:
            model = modelClass
    return DynamicModelSerializer
