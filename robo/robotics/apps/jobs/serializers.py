from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core import fields as core_fields
from core import serializers as core_serializers
from core import mixins as core_mixins
from common import fields as common_fields
from common import enums
from users.serializers import UserSerializer
from orgs.models import Organization
from tasks import serializers as task_serializers
from .models import Job, Application

import logging
logger = logging.getLogger(__name__)


class JobFullCreateSerializer(core_mixins.RequiredFieldsSerializerMixin,
                              core_serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), write_only=True
    )
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    deadline = serializers.DateField(write_only=True)
    keywords = core_fields.ListField(
        child=common_fields.KeywordField(), write_only=True
    )
    word_count = serializers.IntegerField(min_value=0, write_only=True)
    content_type = serializers.ChoiceField(
        choices=enums.WritingContentType.choices(), write_only=True
    )
    goal = serializers.ChoiceField(
        choices=enums.WritingGoal.choices(), write_only=True
    )
    style = serializers.ChoiceField(
        choices=enums.WritingStyle.choices(), write_only=True
    )
    point_of_view = serializers.ChoiceField(
        choices=enums.WritingPointOfView.choices(), write_only=True
    )
    categories = core_fields.ListField(
        child=common_fields.CategoryField(), write_only=True
    )
    can_view = serializers.ChoiceField(
        choices=enums.JobCanView.choices(),write_only=True
    )


    class Meta:
        model = Job
        fields = ('organization', 'title', 'description', 'deadline', 'price',
                  'closing_date', 'keywords', 'word_count', 'content_type',
                  'goal', 'style', 'point_of_view', 'categories', 'can_view')
        required_fields = ('price', 'closing_date')

    def create(self, validated_data):
        task_brief = self.create_task_brief(validated_data)
        task = self.create_task(task_brief, validated_data)
        job = self.create_job(task, validated_data)
        task_brief.published = True
        task_brief.save()
        return job

    def create_task_brief(self, validated_data):
        task_brief_fields = ('creator', 'organization', 'title',
                             'description', 'deadline')
        task_brief_data = {field: validated_data.get(field)
                           for field in task_brief_fields}
        task_brief = task_serializers.TaskBriefSerializer().create(
            task_brief_data
        )
        task_brief.set_keywords(validated_data.get('keywords'))
        task_brief.set_categories(validated_data.get('categories'))
        return task_brief

    def create_task(self, task_brief, validated_data):
        task_fields = ('deadline', 'description', 'word_count',
                       'content_type', 'goal', 'style', 'point_of_view')
        task_data = {field: validated_data.get(field)
                     for field in task_fields}
        task_data.update({'type': enums.TaskType.WRITING,
                          'task_brief': task_brief})
        task = task_serializers.TaskSerializer().create(task_data)
        return task

    def create_job(self, task, validated_data):
        job_fields = ('price', 'closing_date', 'description', 'can_view')
        job_data = {field: validated_data.get(field)
                    for field in job_fields}
        job_data.update({'task': task})
        return super(JobFullCreateSerializer, self).create(job_data)


class JobSerializer(core_serializers.DynamicFieldsModelSerializer):
    task = task_serializers.TaskSerializer(
        read_only=True, exclude_fields=(
            'job', 'assignee', 'task_brief__article',
            'task_brief__task_count', 'task_brief__finished_task_count',
        )
    )
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'price', 'closing_date', 'description',
                  'task', 'creator', 'application_count', 'can_view')
        read_only_fields = ('id', 'task')


class PublishedJobSerializer(core_serializers.InternalDataModelSerializerMixin,
                             core_serializers.RequiredFieldModelSerializer):
    class Meta:
        model = Job
        fields = ('price', 'closing_date')
        required_fields = ('price', 'closing_date')


class ApplicationWriteSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('message', 'status')

    def validate_message(self, message):
        if self.instance:
            if message != self.instance.message:
                raise ValidationError(
                    'Invalid message "%s" - message cannot be changed' %
                    message
                )
        return message

    def validate_status(self, status):
        if self.instance:
            if (status != self.instance.status and
                    status == enums.ApplicationStatus.PENDING):
                raise ValidationError(
                    'Invalid status "%s" - status cannot be changed to \'Pending\'' %
                    status
                )
        else:
            if status != enums.ApplicationStatus.PENDING:
                raise ValidationError(
                    'Invalid status "%s" - new application must have \'Pending\' status' %
                    status
                )
        return status

    def validate(self, data):
        if self.instance and self.instance.status != enums.ApplicationStatus.PENDING:
            raise ValidationError('Non-pending application cannot be modified')
        return data


class ApplicationReadSerializer(core_serializers.ReadOnlyModelSerializer):
    job = JobSerializer(read_only=True)
    applicant = UserSerializer(
        fields=('id', 'first_name', 'last_name',
                'picture', 'description', 'keywords')
    )

    class Meta:
        model = Application
        fields = ('id', 'applicant', 'job', 'status', 'message')
