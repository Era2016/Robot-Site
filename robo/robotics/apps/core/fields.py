from rest_framework import fields
from rest_framework.exceptions import ValidationError


class ListField(fields.ListField):
    def __init__(self, *args, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        return super(ListField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        internal_value = super(ListField, self).to_internal_value(data)
        if not self.allow_blank and not internal_value:
            raise ValidationError("This field must not be empty")
        return internal_value


class ModelField(fields.Field):
    def __init__(self, read_serializer, write_serializer, *args, **kwargs):
        self.read_serializer = read_serializer
        self.write_serializer = write_serializer
        return super(ModelField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        return self.write_serializer.to_internal_value(data)

    def to_representation(self, obj):
        return self.read_serializer.to_representation(obj)

    @property
    def queryset(self):
        return self.read_serializer.queryset

    @queryset.setter
    def queryset(self, value):
        self.read_serializer.queryset = value
