# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_usercode'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercode',
            name='level',
            field=models.TextField(default=b'1', blank=True),
        ),
    ]
