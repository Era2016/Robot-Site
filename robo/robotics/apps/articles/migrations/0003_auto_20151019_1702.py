# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20151019_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='created',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='modified',
        ),
        migrations.AlterField(
            model_name='publication',
            name='image',
            field=models.ImageField(upload_to=b'', blank=True),
        ),
    ]
