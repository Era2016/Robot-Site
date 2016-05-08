# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20151010_1022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='writingtaskmeta',
            old_name='type',
            new_name='content_type',
        ),
    ]
