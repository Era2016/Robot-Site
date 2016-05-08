from core.serializers import ReadOnlyModelSerializer
from .models import Category


class CategorySerializer(ReadOnlyModelSerializer):
    include_timestamp_fields = False

    class Meta:
        model = Category
        fields = ('id', 'name')
