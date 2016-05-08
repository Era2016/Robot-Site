from django.db import models, transaction
from django.db.models import Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model
from notifications import notify
from dirtyfields import DirtyFieldsMixin

from core.models import TimeStampedModel
from common import enums
from tasks.models import Task, TaskBrief, task_brief_published

job_posted = Signal(providing_args=['instance'])
application_accepted = Signal(providing_args=['instance'])
application_rejected = Signal(providing_args=['instance'])


class JobQuerySet(models.QuerySet):
    def created_by(self, user):
        return self.filter(task__task_brief__creator=user)

    def published(self):
        return self.filter(task__task_brief__published=True)

    def prefetch_task_fields(self, exclude=None):
        task_exclude_fields = set(['job', 'assignee_task'])
        task_brief_exclude_fields = set(['article'])
        queryset = (Task.objects.prefetch_common_fields(
                                    exclude=task_exclude_fields)
                                .prefetch_task_brief_fields(
                                    exclude=task_brief_exclude_fields,
                                    annotate_task_stats=False))
        return self.prefetch_related(Prefetch('task', queryset=queryset))


@python_2_unicode_compatible
class Job(TimeStampedModel):
    task = models.OneToOneField(Task)
    price = models.PositiveIntegerField(null=True)
    closing_date = models.DateField(null=True)
    description = models.TextField(blank=True)
    objects = JobQuerySet.as_manager()
    can_view =  models.PositiveIntegerField(
        choices=enums.JobCanView.choices(),
        default = enums.JobCanView.EXTERNAL,
        blank = True,
        null = True
    )

    def creator(self):
        return self.task.task_brief.creator

    def title(self):
        return self.task.task_brief.title

    def is_published(self):
        return self.task.task_brief.published

    def application_count(self):
        return self.applications.count()

    def applied_by(self, user):
        return self.applications.filter(applicant=user).count()

    def accepted_applicant(self):
        try:
            accepted_application = self.applications.get(
                status=enums.ApplicationStatus.ACCEPTED
            )
            return accepted_application.applicant
        except:
            return None

    def __str__(self):
        return self.task.__str__()


@python_2_unicode_compatible
class Application(DirtyFieldsMixin, TimeStampedModel):
    job = models.ForeignKey(Job, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.PositiveSmallIntegerField(
        choices=enums.ApplicationStatus.choices(),
        default=enums.ApplicationStatus.PENDING
    )
    message = models.TextField(max_length=1500)

    class Meta:
        unique_together = (('job', 'applicant'),)

    def save(self, *args, **kwargs):
        just_accepted, just_rejected = False, False
        if 'status' in self.get_dirty_fields():
            just_accepted = self.status == enums.ApplicationStatus.ACCEPTED
            just_rejected = self.status == enums.ApplicationStatus.REJECTED

        ret = super(Application, self).save(*args, **kwargs)

        if just_accepted:
            application_accepted.send(sender=self.__class__, instance=self)
        if just_rejected:
            application_rejected.send(sender=self.__class__, instance=self)

        return ret

    def __str__(self):
        return self.job.__str__()


@receiver(post_save, sender=Application)
def notify_new_application(sender, instance, created, **kwargs):
    if created:
        notify.send(
            instance.applicant, recipient=instance.job.creator(),
            verb=enums.NotificationVerb.APPLICATION_APPLIED,
            action_object=instance, description=instance.message,
            target=instance.job
        )


@receiver(application_accepted, sender=Application)
def notify_application_accepted(sender, instance, **kwargs):
    notify.send(
        instance.job.creator(), recipient=instance.applicant,
        verb=enums.NotificationVerb.APPLICATION_ACCEPTED,
        action_object=instance, description=instance.message,
        target=instance.job
    )


@receiver(application_rejected, sender=Application)
def notify_application_rejected(sender, instance, **kwargs):
    notify.send(
        instance.job.creator(), recipient=instance.applicant,
        verb=enums.NotificationVerb.APPLICATION_REJECTED,
        action_object=instance, description=instance.message,
        target=instance.job
    )


@receiver(application_accepted, sender=Application)
def assign_accepted_applicant_to_job_task(sender, instance, **kwargs):
    job, task = instance.job, instance.job.task
    task.set_assignee(instance.applicant, job.creator())


# Automatically reject all pending applicants if one is accepted
@receiver(application_accepted, sender=Application)
@transaction.atomic
def reject_unaccepted_applicants(sender, instance, **kwargs):
    pending_applications = instance.job.applications.filter(
        status=enums.ApplicationStatus.PENDING
    )
    pending_applications.update(status=enums.ApplicationStatus.REJECTED)
    # loop over pending_applications instead of calling
    # pending_applications so that save is triggered which
    # send the signal for notification
    for application in pending_applications:
        application.status = enums.ApplicationStatus.REJECTED
        application.save()


@receiver(task_brief_published, sender=TaskBrief)
def check_job_posted_signal(sender, instance, **kwargs):
    for task in instance.tasks():
        if hasattr(task, 'job'):
            job_posted.send(sender=task.job.__class__, instance=task.job)


@receiver(job_posted, sender=Job)
def notify_job_posted(sender, instance, **kwargs):
    User = get_user_model()
    writers = User.objects.filter(userrole__role=enums.UserRole.WRITER)
    for writer in writers:
        notify.send(
            instance.creator(), recipient=writer,
            verb=enums.NotificationVerb.JOB_POSTED,
            action_object=instance
        )
