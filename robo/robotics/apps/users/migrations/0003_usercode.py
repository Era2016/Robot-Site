# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20151016_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCode',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('code', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
