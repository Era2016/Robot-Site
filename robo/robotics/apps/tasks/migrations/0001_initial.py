# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dirtyfields.dirtyfields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, b'Writing'), (2, b'Accept')])),
                ('deadline', models.DateField(null=True, blank=True)),
                ('description', models.TextField(max_length=1500, blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Inactive'), (2, b'Active'), (3, b'Finished')])),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TaskAssignee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('assignee', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('task', models.OneToOneField(related_name='assignee_task', to='tasks.Task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskBrief',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=254, blank=True)),
                ('description', models.TextField(max_length=1500, blank=True)),
                ('deadline', models.DateField(null=True, blank=True)),
                ('published', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(to='orgs.Organization', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TaskBriefCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(to='common.Category')),
                ('task_brief', models.ForeignKey(related_name='category_set', to='tasks.TaskBrief')),
            ],
        ),
        migrations.CreateModel(
            name='TaskDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('predecessor', models.ForeignKey(related_name='successor_tasks', to='tasks.Task', unique=True)),
                ('successor', models.ForeignKey(related_name='predecessor_tasks', to='tasks.Task', unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WritingTaskMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('word_count', models.PositiveIntegerField()),
                ('task', models.OneToOneField(related_name='writing_meta', to='tasks.Task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='task',
            name='task_brief',
            field=models.ForeignKey(to='tasks.TaskBrief'),
        ),
        migrations.AlterUniqueTogether(
            name='taskbriefcategory',
            unique_together=set([('task_brief', 'category')]),
        ),
    ]
