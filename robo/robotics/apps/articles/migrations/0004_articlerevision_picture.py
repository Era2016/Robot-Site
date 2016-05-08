# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20151019_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlerevision',
            name='picture',
            field=models.ImageField(upload_to=b'article_images', blank=True),
        ),
    ]
