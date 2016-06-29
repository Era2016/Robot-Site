# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_usercode_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('name', models.TextField(max_length=100, blank=True)),
                ('gender', models.TextField(max_length=100, blank=True)),
                ('title', models.TextField(max_length=100, blank=True)),
                ('email', models.TextField(max_length=120, blank=True)),
                ('telephone', models.TextField(max_length=100, blank=True)),
                ('organization', models.TextField(max_length=256, blank=True)),
                ('designation', models.TextField(max_length=128, blank=True)),
                ('city', models.TextField(max_length=100, blank=True)),
                ('country', models.TextField(max_length=100, blank=True)),
                ('platform', models.TextField(max_length=100, blank=True)),
                ('purpose', models.TextField(blank=True)),
                ('competition_date_from', models.DateTimeField(blank=True)),
                ('competition_date_to', models.DateTimeField(blank=True)),
                ('code', models.TextField(max_length=100, blank=True)),
                ('valid', models.TextField(max_length=100, blank=True)),
                ('mentor_name', models.TextField(max_length=128, blank=True)),
                ('mentor_email', models.TextField(max_length=128, blank=True)),
                ('activation_count', models.IntegerField(default=0, blank=True)),
                ('activation_max', models.IntegerField(default=1, blank=True)),
                ('submit_time', models.DateTimeField(blank=True)),
                ('expiry_date', models.DateTimeField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
