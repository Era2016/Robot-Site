# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_auto_20151029_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='task',
            field=models.ForeignKey(related_name='ratings', to='tasks.Task'),
        ),
    ]
