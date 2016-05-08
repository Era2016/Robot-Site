# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('rater', 'task')]),
        ),
    ]
