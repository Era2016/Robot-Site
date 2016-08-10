from django.contrib.auth import get_user_model
from rest_framework import serializers
from notifications.models import Notification

from core import serializers as core_serializers
from core import fields as core_fields
from common import fields as common_fields
from common import enums
from .models import UserProfile, UserCode

# Custom user model
User = get_user_model()


class UserProfileSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('gender', 'description', 'picture', 'website')
        read_only_fields = ('picture',)


class UserCodeSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = UserCode
        fields = ('code', 'level')
        

class UserSerializer(core_serializers.DynamicFieldsModelSerializer):
    gender = serializers.CharField(
        source='userprofile.gender', read_only=True
    )
    website = serializers.URLField(
        source='userprofile.website', read_only=True
    )
    picture = serializers.ImageField(
        source='userprofile.picture', read_only=True
    )
    description = serializers.CharField(
        source='userprofile.description', read_only=True
    )
    keywords = core_fields.ListField(
        child=common_fields.KeywordField(), read_only=True
    )
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'website', 'gender', 'picture',
                  'description', 'keywords',
                  'rating', 'rating_count')
        read_only_fields = ('id', 'username')

    def get_rating(self, user):
        return user._rating if hasattr(user, '_rating') else None

    def get_rating_count(self, user):
        return (user._rating__count
                if hasattr(user, '_rating__count')
                else None)


class UserPictureSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('picture',)


class NotificationSerializer(core_serializers.ReadOnlyModelSerializer):
    actor = UserSerializer(fields=('id', 'username', 'first_name', 'last_name', 'picture'))
    action_object = serializers.PrimaryKeyRelatedField(read_only=True)
    target = serializers.PrimaryKeyRelatedField(read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'level', 'actor', 'verb', 'description',
                  'action_object', 'target', 'timestamp', 'unread', 'summary')

    def get_summary(self, notification):
        if notification.verb == enums.NotificationVerb.JOB_POSTED:
            return self.get_new_job_summary(notification)
        elif notification.verb == enums.NotificationVerb.APPLICATION_APPLIED:
            return self.get_new_application_summary(notification)
        elif notification.verb in enums.NotificationVerb.APPLICATION_VERBS:
            return self.get_application_accepted_or_rejected_summary(notification)
        elif notification.verb == enums.NotificationVerb.TASK_ASSIGNED:
            return self.get_task_assigned_summary(notification)
        elif notification.verb in enums.NotificationVerb.TASK_VERBS:
            return self.get_task_completed_or_returned_summary(notification)
        elif notification.verb == enums.NotificationVerb.RATING_LEFT:
            return self.get_new_rating_summary(notification)
        elif notification.verb == enums.NotificationVerb.COMMENT_POSTED:
            return self.get_new_comment_summary(notification)
        return None

    def get_new_job_summary(self, notification):
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            'a new job',
            notification.action_object.title()
        ))

    def get_new_application_summary(self, notification):
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            'to your job',
            notification.target.title()
        ))

    def get_application_accepted_or_rejected_summary(self, notification):
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            'your application in',
            notification.target.title()
        ))

    def get_task_assigned_summary(self, notification):
        task, assignee = notification.action_object, notification.target
        assignee_name = ('you' if notification.recipient == assignee
                         else notification.target.name())
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            assignee_name,
            'to task',
            enums.TaskType.labels.get(task.type),
            'in',
            task.task_brief.title
        ))

    def get_task_completed_or_returned_summary(self, notification):
        task = notification.action_object
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            'task',
            enums.TaskType.labels.get(task.type),
            'in',
            task.task_brief.title
        ))

    def get_new_rating_summary(self, notification):
        task = notification.target
        target_name = ('you' if notification.recipient == task.assignee()
                       else task.assignee().name())
        return ' '.join((
            notification.actor.name(),
            'left a rating for',
            target_name,
            'for task',
            enums.TaskType.labels.get(task.type),
            'in',
            task.task_brief.title
        ))

    def get_new_comment_summary(self, notification):
        return ' '.join((
            notification.actor.name(),
            notification.verb,
            'in',
            notification.target.title
        ))
