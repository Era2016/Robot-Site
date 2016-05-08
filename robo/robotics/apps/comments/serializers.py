from core import serializers as core_serializers
from users.serializers import UserSerializer
from .models import Comment


class CommentSerializer(core_serializers.ModelSerializer):
    user = UserSerializer(
        read_only=True,
        fields=('id', 'username', 'first_name', 'last_name', 'picture')
    )

    class Meta:
        model = Comment
        fields = ('user', 'content')
        read_only_fields = ('user',)
