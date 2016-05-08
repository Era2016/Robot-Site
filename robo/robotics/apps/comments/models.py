from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications import notify

from core.models import TimeStampedModel
from common import enums


@python_2_unicode_compatible
class Comment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    # content_object must extend CommentContentObjectNotificationMixin
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.user.__str__()


class CommentContentObjectNotificationMixin(object):
    def notification_recipients(self):
        raise NotImplementedError(
            '.notification_recipients() must be overriden in %s'
            % self.__class__.__name__
        )

    def notification_target(self):
        raise NotImplementedError(
            '.notification_target() must be overriden in %s'
            % self.__class__.__name__
        )


@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    if created:
        for recipient in instance.content_object.notification_recipients():
            if recipient != instance.user:
                notify.send(
                    instance.user, recipient=recipient,
                    verb=enums.NotificationVerb.COMMENT_POSTED,
                    action_object=instance,
                    target=instance.content_object.notification_target()
                )
