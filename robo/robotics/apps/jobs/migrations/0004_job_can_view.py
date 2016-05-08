# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_enumfield.enum
import common.enums


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20151015_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='can_view',
            field=models.PositiveIntegerField(default=2, choices=[(1, django_enumfield.enum.Value(b'INTERNAL', 1, b'Internal', common.enums.JobCanView)), (2, django_enumfield.enum.Value(b'EXTERNAL', 2, b'External', common.enums.JobCanView))]),
        ),
    ]
