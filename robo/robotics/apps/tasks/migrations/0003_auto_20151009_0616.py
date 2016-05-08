# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20151008_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writingtaskmeta',
            name='word_count',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
