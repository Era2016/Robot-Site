from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response
from rest_framework import status, mixins


class MultiSerializerViewSetMixin(object):
    """
    Use different serializer class based on
    whetherthe request is write or read operation.
    Only support basic action: list, created, retrieve, update, deletes
    Override serializer_action_classes to specify which serializer to use:
        serializer_action_classes = {
            'write': WriteSerializer,
            'read': ReadSerializer,
            'create': CreateSerializer  # will take priority over 'write'
        }
    """
    serializer_action_classes = None

    def get_serializer_class(self, action=None):
        assert self.serializer_action_classes, (
            "serializer_action_classes not found in %s" %
            self.__class__.__name__
        )

        action = action if action else self.action
        write_actions = ['create', 'update', 'partial_update']
        operation = 'write' if action in write_actions else 'read'
        if action in self.serializer_action_classes:
            return self.serializer_action_classes.get(action)
        elif operation in self.serializer_action_classes:
            return self.serializer_action_classes.get(operation)
        else:
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        action = kwargs.pop('action', None)
        serializer_class = self.get_serializer_class(action=action)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class MultiSerializerCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        read_serializer = self.get_serializer(
            instance=write_serializer.instance, action='retrieve'
        )
        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class MultiSerializerUpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        write_serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)
        read_serializer = self.get_serializer(instance=instance, action='retrieve')
        return Response(read_serializer.data)


class SecuredFieldMixin(object):
    """
    Filters the queryset for a related field to ensure relation validation
    """
    '''
    For every field in secured_fields, there must be an accompanying method
    named get_secured_field_queryset_<field_name> which returns the filtered
    queryset
    '''
    secured_fields = None

    def get_secured_field_queryset(self, field):
        raise NotImplementedError(
            '{cls}.get_secured_field_queryset(field) must be implemented.'.format(
                cls=self.__class__.__name__
            )
        )

    def get_serializer(self, *args, **kwargs):
        assert self.secured_fields is not None, (
            "No secured_fields found in %s" %
            self.__class__.__name__
        )

        serializer = super(SecuredFieldMixin, self).get_serializer(*args, **kwargs)
        if hasattr(serializer, 'many'):
            # Deserialize list, no validation needed
            return serializer

        for field in self.secured_fields:
            if field in serializer.fields:
                queryset = self.get_secured_field_queryset(field)
                assert queryset is not None, (
                    'queryset for secured field %s must not be None' % field
                )
                serializer.fields[field].queryset = queryset

        return serializer


class CreateOnlyFieldMixin(object):
    def __init__(self, *args, **kwargs):
        super(CreateOnlyFieldMixin, self).__init__(*args, **kwargs)

        meta = getattr(self, 'Meta', None)
        create_only_fields = getattr(meta, 'create_only_fields', None)
        fields = set(self.fields.keys())
        for field_name in create_only_fields:
            assert field_name in fields, (
                "Invalid write_only_field %s in %s",
                (field_name, self.__class__.__name__)
            )
            self.fields[field_name].read_only = False


class DynamicFieldsSerializerMixin(object):
    """
    A ModelSerializer that takes an additional `fields` and 'exclude_fields'
    arguments that control which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        exclude_fields = kwargs.pop('exclude_fields', None)

        assert fields is None or exclude_fields is None, (
            'Only one of fields or exclude_fields should be used'
        )

        # Instantiate the superclass normally
        super(DynamicFieldsSerializerMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            self.include_fields(fields)
        if exclude_fields is not None:
            self.exclude_fields(exclude_fields)

    def include_fields(self, fields):
        nested_subfields = self.get_nested_fields(fields)
        existing_fields = set(self.fields.keys())
        allowed_fields = set(list(fields) + nested_subfields.keys())
        for field_name in existing_fields - allowed_fields:
            self.fields.pop(field_name)
        for field_name in nested_subfields:
            field = self.fields.get(field_name)
            field.include_fields(nested_subfields[field_name])

    @staticmethod
    def get_nested_fields(fields):
        nested_fields = [field for field in fields if '__' in field]
        nested_subfields = {}
        for nested_field_name in nested_fields:
            index = nested_field_name.index('__')
            field_name = nested_field_name[:index]
            nested_subfield = nested_field_name[index+2:]
            if field_name in nested_subfields:
                nested_subfields[field_name].append(nested_subfield)
            else:
                nested_subfields[field_name] = [nested_subfield]
        return nested_subfields

    def exclude_fields(self, fields):
        for field_name in fields:
            self.exclude_field(field_name)

    def exclude_field(self, field_name):
        assert field_name in self.fields, (
            "%s is not in %s's fields" %
            (field_name, self.__class__.__name__)
        )
        self.fields.pop(field_name)


class FullWriteSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(FullWriteSerializerMixin, self).__init__(*args, **kwargs)

        for field_name in set(self.fields.keys()):
            self.fields[field_name].read_only = False


class RequiredFieldsSerializerMixin(object):
    """
    A ModelSerializer that turn all required_fields into required
    Useful to enforce required=True on models with draft mode
    """

    def __init__(self, *args, **kwargs):
        super(RequiredFieldsSerializerMixin, self).__init__(*args, **kwargs)
        required_fields = getattr(self.Meta, 'required_fields', None)
        assert required_fields is not None, (
            'required_fields not found in %s' %
            self.__class__.__name__
        )

        all_fields = set(self.fields.keys())
        for field_name in required_fields:
            assert field_name in all_fields, (
                'required field %s not found in %s' %
                (field_name, self.__class__.__name__)
            )
            field = self.fields[field_name]
            field.required = True
            field.allow_blank = False
            field.allow_null = False