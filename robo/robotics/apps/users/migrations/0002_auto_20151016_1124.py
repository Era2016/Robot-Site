# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_enumfield.enum
import common.enums


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, django_enumfield.enum.Value(b'BUSINESS', 1, b'Business', common.enums.UserRole)), (2, django_enumfield.enum.Value(b'WRITER', 2, b'Writer', common.enums.UserRole))]),
        ),
    ]
