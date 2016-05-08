# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_articlerevision_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='picture',
            field=models.ImageField(upload_to=b'article_images', blank=True),
        ),
    ]
