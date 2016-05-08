from collections import OrderedDict

from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from core import serializers as core_serializers
from core import mixins as core_mixins
from core import fields as core_fields
from common import fields as common_fields
from common import enums
from users import serializers as user_serializers
from orgs.models import Organization
from orgs import serializers as org_serializers
from .models import TaskBrief, Task, WritingTaskMeta

User = get_user_model()


class TaskBriefSerializer(core_serializers.DynamicFieldsModelSerializer):
    organization = core_fields.ModelField(
        write_serializer=serializers.PrimaryKeyRelatedField(
            queryset=Organization.objects.all()
        ),
        read_serializer=org_serializers.OrganizationSerializer(
            fields=('id', 'name')
        ),
        required=False, allow_null=True
    )
    keywords = core_fields.ListField(
        child=common_fields.KeywordField(), required=False, allow_blank=True,
        source='keywords.all'
    )
    categories = core_fields.ListField(
        child=common_fields.CategoryField(), required=False, allow_blank=True,
        source='categories.all'
    )
    current_assignee = serializers.PrimaryKeyRelatedField(read_only=True)
    # task brief should not know about article
    article = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TaskBrief
        fields = ('id', 'creator', 'organization', 'title', 'description',
                  'deadline', 'categories', 'keywords', 'published',
                  'task_count', 'finished_task_count', 'article',
                  'current_assignee')
        read_only_fields = ('id', 'creator')

    @transaction.atomic
    def save(self, **kwargs):
        task_brief = super(TaskBriefSerializer, self).save(**kwargs)
        if 'categories' in self.validated_data:
            categories = self.validated_data.get('categories')
            task_brief.set_categories(categories.get('all'))
        if 'keywords' in self.validated_data:
            keywords = self.validated_data.get('keywords')
            task_brief.set_keywords(keywords.get('all'))

    def create(self, validated_data):
        # categories & keywords is handled in save()
        validated_data.pop('categories', None)
        validated_data.pop('keywords', None)
        # ignore published field as it is handled in PublishTaskBriefSerializer
        validated_data.pop('published', None)
        return super(TaskBriefSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # categories & keywords is handled in save()
        validated_data.pop('categories', None)
        validated_data.pop('keywords', None)
        # ignore published field as it is handled in PublishTaskBriefSerializer
        validated_data.pop('published', None)
        return super(TaskBriefSerializer, self).update(instance, validated_data)


class TaskSerializerMetaMixin(object):
    def __init__(self, instance=None, data=empty, **kwargs):
        super(TaskSerializerMetaMixin, self).__init__(instance, data, **kwargs)
        self.meta_serializer = TaskMetaSerializer(instance, data, **kwargs)

    def is_valid(self, raise_exception=False):
        valid = super(TaskSerializerMetaMixin, self).is_valid()
        valid_meta = self.meta_serializer.is_valid()
        if raise_exception and (not valid or not valid_meta):
            raise ValidationError(self.errors)
        return valid and valid_meta

    def save(self, **kwargs):
        instance = super(TaskSerializerMetaMixin, self).save(**kwargs)
        self.meta_serializer.save(instance, **kwargs)
        return instance

    def create(self, validated_data):
        self.meta_serializer.create_actual_meta_serializer(data=validated_data)
        meta_field_names = self.meta_serializer.get_meta_fields().keys()
        meta_data = {field: validated_data.pop(field)
                     for field in meta_field_names if field in validated_data}
        task = super(TaskSerializerMetaMixin, self).create(validated_data)
        self.meta_serializer.update(task, meta_data)
        return task

    def update(self, instance, validated_data):
        self.meta_serializer.create_actual_meta_serializer(
            instance, data=validated_data
        )
        meta_field_names = self.meta_serializer.get_meta_fields().keys()
        meta_data = {field: validated_data.pop(field)
                     for field in meta_field_names if field in validated_data}
        task = super(TaskSerializerMetaMixin, self).update(instance, validated_data)
        self.meta_serializer.update(task, meta_data)
        return task

    @property
    def data(self):
        data = super(TaskSerializerMetaMixin, self).data
        data.update(self.meta_serializer.data)
        return data

    def to_representation(self, data):
        representation = super(TaskSerializerMetaMixin, self).to_representation(data)
        representation.update(self.meta_serializer.to_representation(data))
        return representation

    @property
    def errors(self):
        errors = super(TaskSerializerMetaMixin, self).errors
        errors.update(self.meta_serializer.errors)
        return errors


class TaskSerializer(core_mixins.DynamicFieldsSerializerMixin,
                     TaskSerializerMetaMixin,
                     core_serializers.ModelSerializer):
    task_brief = TaskBriefSerializer(
        fields=('id', 'organization', 'title', 'keywords', 'categories',
                'task_count', 'finished_task_count', 'article')
    )
    assignee = core_fields.ModelField(
        write_serializer=serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all()
        ),
        read_serializer=user_serializers.UserSerializer(
            fields=('id', 'picture', 'first_name', 'last_name')
        ),
        required=False, allow_null=True
    )
    job = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'task_brief', 'type', 'deadline',
                  'description', 'assignee', 'job', 'status')
        read_only_fields = ('id', 'task_brief')

    def get_job(self, task):
        # bad practice, tasks & jobs should not have circular dependency
        from jobs.serializers import JobSerializer
        if hasattr(task, 'job'):
            return JobSerializer(task.job, exclude_fields=('task',)).data
        return None

    def exclude_field(self, field_name):
        task_brief_field_prefix = 'task_brief__'
        if field_name.startswith(task_brief_field_prefix):
            task_brief_field = field_name[len(task_brief_field_prefix):]
            return self.fields.get('task_brief').exclude_field(task_brief_field)
        return super(TaskSerializer, self).exclude_field(field_name)

    def validate_predecessor(self, predecessor):
        if predecessor.type == enums.TaskType.ACCEPT:
            raise ValidationError(
                'Invalid pk "%s" - accept task cannot be set as predecessor' %
                self.get_initial().get('predecessor')
            )
        return predecessor

    def validate_type(self, type):
        if self.instance:
            if type != self.instance.type:
                raise ValidationError(
                    'Invalid type "%s" - type cannot be changed' %
                    self.get_initial().get('type')
                )
        else:
            if type == enums.TaskType.ACCEPT:
                raise ValidationError(
                    'Invalid type "%s" - accept type cannot be created' %
                    self.get_initial().get('type')
                )
        return type

    def validate_status(self, status):
        if self.instance:
            if status != self.instance.status:
                if (status == enums.TaskStatus.INACTIVE and
                        not self.instance.predecessor()):
                    raise ValidationError(
                        'Invalid status "%s" - task without predecessor '
                        'cannot be set to inactive' %
                        self.get_initial().get('status')
                    )
        return status

    def validate(self, data):
        predecessor = data.get('predecessor', None)
        successor = data.get('successor', None)
        if predecessor is not None and successor is not None:
            raise ValidationError(
                'Only one of "predecessor" and "successor" should be provided'
            )

        return data

    @transaction.atomic
    def save(self, **kwargs):
        task = super(TaskSerializer, self).save(**kwargs)
        predecessor = self.validated_data.get('predecessor', None)
        successor = self.validated_data.get('successor', None)

        if predecessor:
            task.set_predecessor(predecessor)
        if successor:
            task.set_successor(successor)
        if 'assignee' in self.validated_data:
            assignee = self.validated_data.get('assignee')
            assigner = kwargs.get('assigner')
            task.set_assignee(assignee, assigner)

        return task

    def create(self, validated_data):
        # predecessor/successor and assignee/assigner are handled in save()
        predecessor = validated_data.pop('predecessor', None)
        successor = validated_data.pop('successor', None)
        validated_data.pop('assignee', None)
        validated_data.pop('assigner', None)
        task = super(TaskSerializer, self).create(validated_data)

        if not predecessor and not successor:
            # Special case: if neither predecessor nor successor is provided
            # make this task the last task in dependency chain (before accept)
            accept_task = task.task_brief.accept_task()
            task.set_successor(accept_task)
        return task

    def update(self, instance, validated_data):
        # predecessor/successor and assignee/assigner are handled in save()
        validated_data.pop('predecessor', None)
        validated_data.pop('successor', None)
        validated_data.pop('assignee', None)
        validated_data.pop('assigner', None)
        return super(TaskSerializer, self).update(instance, validated_data)


class TaskMetaSerializer(core_serializers.ModelSerializer):
    """
    Factory/Abstract factory pattern
    Delegate all validations/save/update to the actual meta serializer
    """
    class Meta:
        model = Task
        fields = ('type',)
        write_only_fields = ('type',)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(TaskMetaSerializer, self).__init__(instance, data, **kwargs)
        self.actual_meta_serializer = None

    def is_valid(self, raise_exception=False):
        valid = super(TaskMetaSerializer, self).is_valid()
        if valid and not self.actual_meta_serializer:
            self.create_actual_meta_serializer(
                self.instance, self.validated_data, self.initial_data
            )
        meta_valid = True
        if self.actual_meta_serializer:
            meta_valid = self.actual_meta_serializer.is_valid()

        if raise_exception and not (valid and meta_valid):
            raise ValidationError(self.errors)
        return valid and meta_valid

    def create_actual_meta_serializer(self, instance=None, data=empty, initial=empty):
        if not self.actual_meta_serializer:
            type = None
            task_meta = None
            if instance:
                type = instance.type
                task_meta = instance.task_meta
            if data is not empty and 'type' in data:
                type = data.get('type')

            if type == enums.TaskType.WRITING:
                self.actual_meta_serializer = WritingTaskMetaSerializer(
                    task_meta, initial
                )

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s, use update() instead' %
            self.__class__.__name__
        )

    def save(self, instance=None, **kwargs):
        # Only update is allowed since TaskMeta is automatically created w task
        if instance and not self.instance:
            self.instance = instance
        if self.instance:
            instance = super(TaskMetaSerializer, self).save(**kwargs)
            if self.actual_meta_serializer:
                if not self.actual_meta_serializer.instance:
                    self.actual_meta_serializer.instance = instance.task_meta
                self.actual_meta_serializer.save(**kwargs)
            return instance
        return None

    def update(self, instance, validated_data):
        if self.actual_meta_serializer:
            self.actual_meta_serializer.update(instance.task_meta, validated_data)
        return instance

    def to_representation(self, data):
        representation = super(TaskMetaSerializer, self).to_representation(data)
        task = data if isinstance(data, Task) else None
        data = data if not isinstance(data, Task) else empty
        # serializer can be reused in List Serializer
        # so we need to force recreate actual_meta_serializer
        # for different type of tasks
        self.actual_meta_serializer = None
        self.create_actual_meta_serializer(task, data)
        if self.actual_meta_serializer:
            if task:
                representation.update(
                    self.actual_meta_serializer.to_representation(task.task_meta)
                )
            else:
                # task meta might have its internal type property
                data.pop('type', None)
                representation.update(
                    self.actual_meta_serializer.to_representation(data)
                )
        return representation

    def get_meta_fields(self):
        if self.actual_meta_serializer:
            return self.actual_meta_serializer.get_fields()
        return {}

    @property
    def data(self):
        data = super(TaskMetaSerializer, self).data
        if self.actual_meta_serializer:
            data.update(self.actual_meta_serializer.data)
        return data

    @property
    def errors(self):
        errors = super(TaskMetaSerializer, self).errors
        if self.actual_meta_serializer:
            errors.update(self.actual_meta_serializer.errors)
        return errors


class WritingTaskMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTaskMeta
        exclude = ('id', 'task', 'created', 'modified')

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s, use update() instead' %
            self.__class__.__name__
        )


class PublishedTaskBriefSerializer(core_serializers.InternalDataModelSerializerMixin,
                                   core_serializers.RequiredFieldModelSerializer):
    # Stricter validation check is needed for published task brief
    # It should only be used for update, and it only updates published attribute

    class Meta:
        model = TaskBrief
        fields = ('organization', 'title', 'description',
                  'deadline', 'categories', 'published')
        required_fields = ('organization', 'title', 'description',
                           'deadline', 'categories', 'published')

    def validate_published(self, published):
        if not published:
            raise ValidationError('Published brief cannot be unpublished')
        return published

    def validate(self, data):
        errors = OrderedDict()
        if self.instance:
            task_errors = []
            for task in self.instance.tasks():
                try:
                    task_serializer = PublishedTaskSerializer(task)
                    task_serializer.is_valid(raise_exception=True)
                except ValidationError as exc:
                    exc.detail.update({'id': task.id})
                    task_errors.append(exc.detail)
            if any(task_errors):
                errors['tasks'] = task_errors

        if errors:
            raise ValidationError(errors)
        return data

    def create(self, validated_data):
        raise AssertionError(
            'create is not allowed in %s' % self.__class__.__name__
        )

    def update(self, instance, validated_data):
        instance.published = True
        instance.save()
        return instance


class PublishedTaskSerializerMetaMixin(object):
    def __init__(self, instance=None, data=empty, **kwargs):
        super(PublishedTaskSerializerMetaMixin, self).__init__(instance, data, **kwargs)
        self.published_meta_serializer = PublishedTaskMetaSerializer(instance, data, **kwargs)

    def is_valid(self, raise_exception=False):
        valid = super(PublishedTaskSerializerMetaMixin, self).is_valid()
        valid_meta = self.published_meta_serializer.is_valid()
        if raise_exception and (not valid or not valid_meta):
            raise ValidationError(self.errors)
        return valid and valid_meta

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s' % self.__class__.__name__
        )

    def update(self, validated_data):
        raise AssertionError(
            'update() is not allowed on %s' % self.__class__.__name__
        )

    @property
    def errors(self):
        errors = super(PublishedTaskSerializerMetaMixin, self).errors
        errors.update(self.published_meta_serializer.errors)
        return errors


class PublishedTaskSerializer(core_serializers.InternalDataModelSerializerMixin,
                              PublishedTaskSerializerMetaMixin,
                              core_serializers.RequiredFieldModelSerializer):
    class Meta:
        model = Task
        fields = ('deadline',)
        required_fields = ('deadline',)

    def validate(self, data):
        # bad practice, tasks & jobs should not have circular dependency
        from jobs.serializers import PublishedJobSerializer

        errors = OrderedDict()
        assert self.instance is not None, (
            'instance (internal data) is required for %s' %
            self.__class__.__name__
        )
        # tasks app should not really know about jobs app here
        if hasattr(self.instance, 'job'):
            job = self.instance.job
            try:
                job_serializer = PublishedJobSerializer(job)
                job_serializer.is_valid(raise_exception=True)
            except ValidationError as exc:
                exc.detail.update({'id': job.id})
                errors['job'] = exc.detail
        if errors:
            raise ValidationError(errors)
        return data

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s' % self.__class__.__name__
        )

    def update(self, validated_data):
        raise AssertionError(
            'update() is not allowed on %s' % self.__class__.__name__
        )


class PublishedTaskMetaSerializer(core_serializers.ModelSerializer):
    """
    Factory/Abstract factory pattern
    Delegate all validations to the actual meta serializer
    """
    class Meta:
        model = Task
        fields = ('type',)
        write_only_fields = ('type',)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(PublishedTaskMetaSerializer, self).__init__(instance, data, **kwargs)
        self.actual_meta_serializer = None

    def is_valid(self, raise_exception=False):
        valid = super(PublishedTaskMetaSerializer, self).is_valid()
        if valid and not self.actual_meta_serializer:
            self.create_actual_meta_serializer(
                self.instance, self.validated_data, self.initial_data
            )
        meta_valid = True
        if self.actual_meta_serializer:
            meta_valid = self.actual_meta_serializer.is_valid()

        if raise_exception and not (valid and meta_valid):
            raise ValidationError(self.errors)
        return valid and meta_valid

    def create_actual_meta_serializer(self, instance=None, data=empty, initial=empty):
        if not self.actual_meta_serializer:
            type = None
            task_meta = None
            if instance:
                type = instance.type
                task_meta = instance.task_meta
            if data is not empty and 'type' in data:
                type = data.get('type')

            if type == enums.TaskType.WRITING:
                self.actual_meta_serializer = PublishedWritingTaskMetaSerializer(
                    task_meta, initial
                )

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s' %
            self.__class__.__name__
        )

    @property
    def errors(self):
        errors = super(PublishedTaskMetaSerializer, self).errors
        if self.actual_meta_serializer:
            errors.update(self.actual_meta_serializer.errors)
        return errors

    def update(self, validated_data):
        raise AssertionError(
            'update() is not allowed on %s' % self.__class__.__name__
        )


class PublishedWritingTaskMetaSerializer(core_serializers.InternalDataModelSerializerMixin,
                                         core_serializers.RequiredFieldModelSerializer):
    content_type = serializers.ChoiceField(
        choices=enums.WritingContentType.choices(),
    )

    class Meta:
        model = WritingTaskMeta
        exclude = ('id', 'task')
        required_fields = ('word_count', 'content_type',
                           'goal', 'style', 'point_of_view')

    def create(self, validated_data):
        raise AssertionError(
            'create() is not allowed on %s' % self.__class__.__name__
        )

    def update(self, validated_data):
        raise AssertionError(
            'update() is not allowed on %s' % self.__class__.__name__
        )
