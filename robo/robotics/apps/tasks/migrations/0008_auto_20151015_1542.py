# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0007_auto_20151012_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskassignee',
            name='assigner',
            field=models.ForeignKey(related_name='taskassigner', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='taskassignee',
            name='assignee',
            field=models.ForeignKey(related_name='taskassignee', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
