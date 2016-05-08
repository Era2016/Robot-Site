# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('website', models.URLField()),
                ('description', models.TextField()),
                ('picture', models.ImageField(upload_to=b'org_images', blank=True)),
                ('year_founded', models.IntegerField()),
                ('size', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('user_role', models.PositiveSmallIntegerField(choices=[(1, b'Owner'), (2, b'Employee')])),
                ('organization', models.ForeignKey(to='orgs.Organization')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='organizationuser',
            unique_together=set([('user', 'organization')]),
        ),
    ]
