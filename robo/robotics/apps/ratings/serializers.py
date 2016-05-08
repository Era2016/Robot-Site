from core import serializers as core_serializers
from users.serializers import UserSerializer
from tasks.serializers import TaskSerializer
from .models import Rating


class RatingSerializer(core_serializers.ModelSerializer):
    # workaround: django rest mark all fields in unique_together as 'required'
    # even though they're read_only, so add default=None to workaround that
    rater = UserSerializer(
        fields=('id', 'username', 'first_name', 'last_name', 'picture'),
        read_only=True, default=None
    )
    task = TaskSerializer(fields=('id', 'type'), read_only=True, default=None)

    class Meta:
        model = Rating
        read_only_fields = ('id',)
