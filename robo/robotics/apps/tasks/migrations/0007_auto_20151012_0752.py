# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_keyword'),
        ('tasks', '0006_auto_20151011_0414'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskbrief',
            name='categories',
            field=models.ManyToManyField(to='common.Category', through='tasks.TaskBriefCategory'),
        ),
        migrations.AddField(
            model_name='taskbrief',
            name='keywords',
            field=models.ManyToManyField(to='common.Keyword', through='tasks.TaskBriefKeyword'),
        ),
    ]
