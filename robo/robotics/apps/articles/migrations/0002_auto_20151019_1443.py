# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_delete_industry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=256)),
                ('content', models.TextField()),
                ('image', models.URLField(blank=True)),
                ('publish_date', models.DateTimeField(null=True, blank=True)),
                ('keywords', models.ManyToManyField(related_name='articles', to='common.Keyword')),
                ('meta_keywords', models.ManyToManyField(related_name='meta_articles', to='common.Keyword')),
                ('news_keywords', models.ManyToManyField(related_name='news_articles', to='common.Keyword')),
                ('nlp_keywords', models.ManyToManyField(related_name='nlp_articles', to='common.Keyword')),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(unique=True)),
                ('name', models.CharField(max_length=256, blank=True)),
                ('image', models.URLField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='importedarticle',
            name='publication',
            field=models.ForeignKey(related_name='articles', to='articles.Publication'),
        ),
        migrations.AddField(
            model_name='importedarticle',
            name='user',
            field=models.ForeignKey(related_name='articles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='importedarticle',
            unique_together=set([('user', 'url')]),
        ),
    ]
