# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_keyword'),
        ('tasks', '0003_auto_20151009_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskBriefKeyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('keyword', models.ForeignKey(to='common.Keyword')),
                ('task_brief', models.ForeignKey(related_name='keyword_set', to='tasks.TaskBrief')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='taskbriefkeyword',
            unique_together=set([('task_brief', 'keyword')]),
        ),
    ]
