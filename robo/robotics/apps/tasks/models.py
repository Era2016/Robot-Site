from django.db import models, transaction
from django.db.models import Count, Prefetch
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import python_2_unicode_compatible
from django.dispatch import receiver, Signal
from django.contrib.contenttypes.fields import GenericRelation
from notifications import notify
from dirtyfields import DirtyFieldsMixin

from core.models import TimeStampedModel
from common.models import Category, Keyword
from common import enums
from comments.models import Comment, CommentContentObjectNotificationMixin
from orgs.models import Organization

task_brief_published = Signal(providing_args=['instance'])
task_inactive = Signal(providing_args=['instance'])
task_finished = Signal(providing_args=['instance'])
task_assigned = Signal(providing_args=['instance'])


class TaskBriefQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)

    def created_by(self, user):
        return self.filter(creator=user)

    def in_organization(self, organization):
        return self.filter(organization=organization)

    def prefetch_common_fields(self, exclude=None):
        related_fields = set(['organization', 'keywords', 'categories', 'article'])
        if exclude:
            related_fields = related_fields - set(exclude)
        return self.prefetch_related(*related_fields)

    def annotate_task_stats(self):
        return self.annotate(Count('task')).extra(select={
            'finished_task__count': """
            SELECT COUNT(*)
            FROM tasks_task
            WHERE tasks_task.task_brief_id = tasks_taskbrief.id
            AND tasks_task.status = %d
            """ % enums.TaskStatus.FINISHED
        })


@python_2_unicode_compatible
class TaskBrief(DirtyFieldsMixin,
                CommentContentObjectNotificationMixin,
                TimeStampedModel):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    organization = models.ForeignKey(Organization, null=True)

    title = models.CharField(max_length=254, blank=True)
    description = models.TextField(max_length=1500, blank=True)
    deadline = models.DateField(null=True, blank=True)
    published = models.BooleanField(default=False)

    keywords = models.ManyToManyField(Keyword, through='TaskBriefKeyword')
    categories = models.ManyToManyField(Category, through='TaskBriefCategory')
    comments = GenericRelation(Comment)

    objects = TaskBriefQuerySet.as_manager()

    def save(self, *args, **kwargs):
        just_published = False
        if 'published' in self.get_dirty_fields() and self.published:
            just_published = True
        ret = super(TaskBrief, self).save(*args, **kwargs)
        if just_published:
            task_brief_published.send(sender=self.__class__, instance=self)
        return ret

    def set_keywords(self, keywords):
        old_keywords = self.keywords.all()
        for keyword in old_keywords:
            if not keywords or keyword not in keywords:
                self._remove_keyword(keyword)
        if keywords:
            for keyword in keywords:
                if keyword not in old_keywords:
                    self._add_keyword(keyword)

    def _add_keyword(self, keyword):
        TaskBriefKeyword.objects.create(task_brief=self, keyword=keyword)

    def _remove_keyword(self, keyword):
        TaskBriefKeyword.objects.filter(task_brief=self, keyword=keyword).delete()

    def set_categories(self, categories):
        old_categories = self.categories.all()
        for category in old_categories:
            if not categories or category not in categories:
                self._remove_category(category)
        if categories:
            for category in categories:
                if category not in old_categories:
                    self._add_category(category)

    def _add_category(self, category):
        TaskBriefCategory.objects.create(task_brief=self, category=category)

    def _remove_category(self, category):
        TaskBriefCategory.objects.filter(task_brief=self, category=category).delete()

    def task_count(self):
        if hasattr(self, 'task__count'):
            return self.task__count
        return self.task_set.count()

    def finished_task_count(self):
        if hasattr(self, 'finished_task__count'):
            return self.finished_task__count
        return self.task_set.filter(status=enums.TaskStatus.FINISHED).count()

    def tasks(self):
        return self.task_set.all()

    def ordered_tasks(self):
        ordered_tasks = []
        task = self.first_task()
        while task:
            ordered_tasks.append(task)
            task = task.successor()
        return ordered_tasks

    def first_task(self):
        return self.task_set.get(predecessor_tasks=None)

    def current_task(self):
        try:
            return self.task_set.get(status=enums.TaskStatus.ACTIVE)
        except Task.DoesNotExist:
            return None

    def accept_task(self):
        return self.task_set.get(type=enums.TaskType.ACCEPT)

    def finished(self):
        return self.accept_task().status == enums.TaskStatus.FINISHED

    def current_assignee(self):
        current_task = self.current_task()
        if current_task:
            return current_task.assignee()
        return None

    def has_assignee(self, assignee):
        return bool(TaskAssignee.objects.filter(task__in=self.task_set.all(),
                                                assignee=assignee)
                                        .count())

    def assignees(self):
        User = get_user_model()
        return User.objects.filter(taskassignees__task__task_brief=self).distinct()

    def notification_recipients(self):
        return self.assignees()

    def notification_target(self):
        return self

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class TaskBriefCategory(TimeStampedModel):
    task_brief = models.ForeignKey(TaskBrief, related_name='category_set')
    category = models.ForeignKey(Category)

    class Meta:
        unique_together = (('task_brief', 'category'),)

    def __str__(self):
        return self.task_brief.__str__()


@python_2_unicode_compatible
class TaskBriefKeyword(TimeStampedModel):
    task_brief = models.ForeignKey(TaskBrief, related_name='keyword_set')
    keyword = models.ForeignKey(Keyword)

    class Meta:
        unique_together = (('task_brief', 'keyword'),)

    def __str__(self):
        return self.task_brief.__str__()


class TaskQuerySet(models.QuerySet):
    def published(self):
        return self.filter(task_brief__published=True)

    def assigned_to(self, user):
        return self.filter(assignee_task__assignee=user)

    def in_organization(self, organization):
        return self.filter(task_brief__organization=organization)

    def prefetch_common_fields(self, exclude=None):
        related_fields = set(['writing_meta', 'job', 'assignee_task'])
        if exclude:
            related_fields = related_fields - set(exclude)
        return self.prefetch_related(*related_fields)

    def prefetch_task_brief_fields(self, exclude=None, annotate_task_stats=True):
        queryset = TaskBrief.objects.prefetch_common_fields(exclude=exclude)
        if annotate_task_stats:
            queryset = queryset.annotate_task_stats()
        return self.prefetch_related(Prefetch('task_brief', queryset=queryset))


@python_2_unicode_compatible
class Task(DirtyFieldsMixin, TimeStampedModel):
    task_brief = models.ForeignKey(TaskBrief)
    type = models.PositiveSmallIntegerField(choices=enums.TaskType.choices())
    deadline = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=1500, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=enums.TaskStatus.choices(), default=enums.TaskStatus.INACTIVE
    )

    objects = TaskQuerySet.as_manager()

    def save(self, *args, **kwargs):
        just_inactive, just_finished = False, False
        if 'status' in self.get_dirty_fields():
            just_inactive = self.status == enums.TaskStatus.INACTIVE
            just_finished = self.status == enums.TaskStatus.FINISHED
        ret = super(Task, self).save(*args, **kwargs)
        if just_inactive:
            task_inactive.send(sender=self.__class__, instance=self)
        if just_finished:
            task_finished.send(sender=self.__class__, instance=self)
        return ret

    def delete(self, *args, **kwargs):
        self._detach_from_dependency_chain()
        return super(Task, self).delete(*args, **kwargs)

    @property
    def task_meta(self):
        if self.type == enums.TaskType.WRITING:
            return self.writing_meta
        return None

    def assigner(self):
        return self.assignee_task.assigner

    def assignee(self):
        return self.assignee_task.assignee

    def set_assignee(self, assignee, assigner):
        self.assignee_task.assignee = assignee
        self.assignee_task.assigner = assigner
        self.assignee_task.save()

    def predecessor(self):
        try:
            return self.predecessor_tasks.first().predecessor
        except AttributeError:
            return None

    def successor(self):
        try:
            return self.successor_tasks.first().successor
        except AttributeError:
            return None

    @transaction.atomic
    def set_predecessor(self, predecessor):
        if predecessor != self.predecessor():
            assert predecessor is not None, 'predecessor must not be None'
            self._detach_from_dependency_chain()
            self._set_predecessor(predecessor)

    @transaction.atomic
    def set_successor(self, successor):
        if successor != self.successor():
            assert successor is not None, 'successor must not be None'
            self._detach_from_dependency_chain()
            self._set_successor(successor)

    @transaction.atomic
    def _detach_from_dependency_chain(self):
        predecessor = self.predecessor()
        successor = self.successor()
        if predecessor:
            self.predecessor_tasks.first().delete()
        if successor:
            self.successor_tasks.first().delete()
        if predecessor and successor:
            TaskDependency.objects.create(
                predecessor=predecessor, successor=successor
            )

    @transaction.atomic
    def _set_predecessor(self, predecessor):
        successor = predecessor.successor()
        if successor:
            predecessor.successor_tasks.first().delete()
            TaskDependency.objects.create(predecessor=self, successor=successor)
        TaskDependency.objects.create(predecessor=predecessor, successor=self)

    @transaction.atomic
    def _set_successor(self, successor):
        predecessor = successor.predecessor()
        if predecessor:
            successor.predecessor_tasks.first().delete()
            TaskDependency.objects.create(predecessor=predecessor, successor=self)
        TaskDependency.objects.create(predecessor=self, successor=successor)

    def __str__(self):
        return self.task_brief.__str__()


@python_2_unicode_compatible
class WritingTaskMeta(TimeStampedModel):
    task = models.OneToOneField(Task, related_name='writing_meta')
    word_count = models.PositiveIntegerField(blank=True, null=True)
    content_type = models.PositiveSmallIntegerField(
        choices=enums.WritingContentType.choices(), blank=True, null=True
    )
    goal = models.PositiveIntegerField(
        choices=enums.WritingGoal.choices(), blank=True, null=True
    )
    style = models.PositiveIntegerField(
        choices=enums.WritingStyle.choices(), blank=True, null=True
    )
    point_of_view = models.PositiveIntegerField(
        choices=enums.WritingPointOfView.choices(), blank=True, null=True
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.task.__str__()


@python_2_unicode_compatible
class TaskDependency(DirtyFieldsMixin, TimeStampedModel):
    # ForeignKey is used instead of OneToOneField because Django 'hard' caches
    # one-to-one property and do not automatically refresh it when deletion occurs
    # This makes it hard to dynamically alter the dependency chain
    # i.e. predecessor_task & successor_task still exist after deletion (due to cache)
    predecessor = models.ForeignKey(Task, unique=True, related_name='successor_tasks')
    successor = models.ForeignKey(Task, unique=True, related_name='predecessor_tasks')

    def __str__(self):
        return self.task.__str__()


@python_2_unicode_compatible
class TaskAssignee(DirtyFieldsMixin, TimeStampedModel):
    task = models.OneToOneField(Task, related_name='assignee_task')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='taskassignees'
    )
    assigner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='taskassigners'
    )

    def save(self, *args, **kwargs):
        just_assigned = False
        if 'assignee' in self.get_dirty_fields(check_relationship=True):
            just_assigned = True
        ret = super(TaskAssignee, self).save(*args, **kwargs)
        if just_assigned:
            task_assigned.send(sender=self.__class__, instance=self)
        return ret

    def __str__(self):
        return self.task.__str__()


@receiver(post_save, sender=TaskBrief)
def create_brief_accept_task(sender, instance, created, **kwargs):
    if created:
        task = Task.objects.create(
            type=enums.TaskType.ACCEPT, task_brief=instance,
            deadline=instance.deadline
        )
        task.set_assignee(instance.creator, instance.creator)
    else:
        accept_task = instance.accept_task()
        accept_task.deadline = instance.deadline
        accept_task.save()


@receiver(task_brief_published, sender=TaskBrief)
def start_brief_first_task(sender, instance, **kwargs):
    first_task = instance.first_task()
    first_task.status = enums.TaskStatus.ACTIVE
    first_task.save()


@receiver(task_finished, sender=Task)
def start_successor_task(sender, instance, **kwargs):
    successor = instance.successor()
    if successor:
        successor.status = enums.TaskStatus.ACTIVE
        successor.save()


@receiver(task_inactive, sender=Task)
def start_predecessor_task(sender, instance, **kwargs):
    predecessor = instance.predecessor()
    if predecessor:
        predecessor.status = enums.TaskStatus.ACTIVE
        predecessor.save()


@receiver(post_save, sender=Task)
def create_task_assignee(sender, instance, created, **kwargs):
    if created:
        TaskAssignee.objects.create(task=instance)


@receiver(post_save, sender=Task)
def create_task_meta(sender, instance, created, **kwargs):
    if created:
        if instance.type == enums.TaskType.WRITING:
            WritingTaskMeta.objects.create(task=instance)


@receiver(task_brief_published, sender=TaskBrief)
def notify_brief_assignees(sender, instance, **kwargs):
    for task in instance.tasks():
        assignee = task.assignee()
        if assignee and assignee != instance.creator:
            notify.send(
                instance.creator, recipient=assignee,
                verb=enums.NotificationVerb.TASK_ASSIGNED,
                action_object=task, target=assignee
            )


@receiver(task_assigned, sender=TaskAssignee)
def notify_task_assigned(sender, instance, **kwargs):
    if instance.task.task_brief.published:
        for assignee in instance.task.task_brief.assignees():
            if assignee != instance.assigner:
                notify.send(
                    instance.assigner, recipient=assignee,
                    verb=enums.NotificationVerb.TASK_ASSIGNED,
                    action_object=instance.task, target=instance.assignee
                )


@receiver(task_finished, sender=Task)
def notify_task_completed(sender, instance, **kwargs):
    for assignee in instance.task_brief.assignees():
        if assignee != instance.assignee():
            notify.send(
                instance.assignee(), recipient=assignee,
                verb=enums.NotificationVerb.TASK_COMPLETED,
                action_object=instance
            )


@receiver(task_inactive, sender=Task)
def notify_task_returned(sender, instance, **kwargs):
    for assignee in instance.task_brief.assignees():
        if assignee != instance.assignee():
            notify.send(
                instance.assignee(), recipient=assignee,
                verb=enums.NotificationVerb.TASK_RETURNED,
                action_object=instance
            )
