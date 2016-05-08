# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20151016_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskassignee',
            name='assignee',
            field=models.ForeignKey(related_name='taskassignees', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='taskassignee',
            name='assigner',
            field=models.ForeignKey(related_name='taskassigners', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
