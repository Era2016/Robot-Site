# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_enumfield.enum
import common.enums


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20151010_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='status',
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, django_enumfield.enum.Value(b'PENDING', 1, b'Pending', common.enums.ApplicationStatus)), (2, django_enumfield.enum.Value(b'REJECTED', 2, b'Rejected', common.enums.ApplicationStatus)), (3, django_enumfield.enum.Value(b'ACCEPTED', 3, b'Accepted', common.enums.ApplicationStatus))]),
        ),
    ]
