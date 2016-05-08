# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_enumfield.enum
import common.enums


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20151010_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, django_enumfield.enum.Value(b'WRITING', 1, b'Writing', common.enums.TaskType)), (2, django_enumfield.enum.Value(b'ACCEPT', 2, b'Accept', common.enums.TaskType))]),
        ),
    ]