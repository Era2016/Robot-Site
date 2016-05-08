from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Keyword, Category


class CategoryField(serializers.Field):
    def to_representation(self, category):
        return category.name

    def to_internal_value(self, category_pk):
        category_pk = serializers.IntegerField().to_internal_value(category_pk)
        try:
            return Category.objects.get(pk=category_pk)
        except Category.DoesNotExist:
            raise ValidationError('Invalid category "%s"' % category_pk)


class KeywordField(serializers.CharField):
    def to_representation(self, keyword):
        return keyword.name

    def to_internal_value(self, keyword_str):
        keyword_str = super(KeywordField, self).to_internal_value(keyword_str)
        if not keyword_str:
            raise ValidationError('Invalid keyword "%s"' % keyword_str)

        keyword_max_length = Keyword._meta.get_field('name').max_length
        if len(keyword_str) > keyword_max_length:
            raise ValidationError(
                'Keyword too long "%s", max length is %d' %
                (keyword_str, keyword_max_length)
            )

        keyword_slug = keyword_str.lower()
        try:
            return Keyword.objects.get(name=keyword_slug)
        except Keyword.DoesNotExist:
            return Keyword.objects.create(name=keyword_slug)
