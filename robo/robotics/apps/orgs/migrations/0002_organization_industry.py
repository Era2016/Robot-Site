# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='industry',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
