from django import forms
from django.utils.encoding import force_str
from django.utils.dateparse import parse_datetime

import django_filters
from rest_framework import ISO_8601


# IsoDateTimeField/PreciseDateTimeField/IsoDateTimeFilter/PreciseDateTimeFilter
# are taken from https://gist.github.com/copitux/5773821
class IsoDateTimeField(forms.DateTimeField):
    """
    It support 'iso-8601' date format too which is out the scope of
    the ``datetime.strptime`` standard library

    # ISO 8601: ``http://www.w3.org/TR/NOTE-datetime``
    """
    def strptime(self, value, format):
        value = force_str(value)
        if format == ISO_8601:
            parsed = parse_datetime(value)
            if parsed is None:  # Continue with other formats if doesn't match
                raise ValueError
            return parsed
        return super(IsoDateTimeField, self).strptime(value, format)


class PreciseDateTimeField(IsoDateTimeField):
    """ Only support ISO 8601 """
    def __init__(self, *args, **kwargs):
        kwargs['input_formats'] = (ISO_8601, )
        super(PreciseDateTimeField, self).__init__(*args, **kwargs)


class IsoDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter by ISO 8601 formated dates too"""
    field_class = IsoDateTimeField


class PreciseDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter only by ISO 8601 formated dates """
    field_class = PreciseDateTimeField
