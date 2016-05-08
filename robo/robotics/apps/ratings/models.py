from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications import notify

from core.models import TimeStampedModel
from common import enums
from tasks.models import Task


class RatingQuerySet(models.QuerySet):
    def prefetch_common_fields(self, exclude=None):
        related_fields = set(['rater', 'rater__userprofile'])
        if exclude:
            related_fields = related_fields - set(exclude)
        return self.prefetch_related(*related_fields)

    def in_brief(self, task_brief):
        return self.filter(task__task_brief=task_brief)

    def has_ratee(self, user):
        return self.filter(task__assignee_task__assignee=user)


class Rating(TimeStampedModel):
    rater = models.ForeignKey(settings.AUTH_USER_MODEL)
    task = models.ForeignKey(Task, related_name='ratings')
    overall_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.CharField(max_length=1000)
    quality_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True
    )
    accessibility_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True
    )
    speed_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True
    )

    objects = RatingQuerySet.as_manager()

    class Meta:
        unique_together = (('rater', 'task'),)

    @property
    def ratee(self):
        return self.task.assignee


@receiver(post_save, sender=Rating)
def notify_rating_left(sender, instance, created, **kwargs):
    if created:
        for assignee in instance.task.task_brief.assignees():
            notify.send(
                instance.rater, recipient=assignee,
                verb=enums.NotificationVerb.RATING_LEFT,
                action_object=instance, target=instance.task
            )
