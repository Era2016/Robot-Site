# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0003_auto_20151009_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pending'), (2, b'Rejected'), (3, b'Accepted')])),
                ('message', models.TextField(max_length=1500)),
                ('applicant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('price', models.PositiveIntegerField(null=True)),
                ('closing_date', models.DateField(null=True)),
                ('description', models.TextField(blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, 1), (2, 2)])),
                ('task', models.OneToOneField(to='tasks.Task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='application',
            name='job',
            field=models.ForeignKey(to='jobs.Job'),
        ),
        migrations.AlterUniqueTogether(
            name='application',
            unique_together=set([('job', 'applicant')]),
        ),
    ]
