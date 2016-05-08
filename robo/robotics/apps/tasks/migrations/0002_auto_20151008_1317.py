# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_enumfield.enum
import common.enums


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='writingtaskmeta',
            name='goal',
            field=models.PositiveIntegerField(blank=True, null=True, choices=[(1, django_enumfield.enum.Value(b'GENERATE_CLICKS', 1, b'Generate Clicks', common.enums.WritingGoal)), (2, django_enumfield.enum.Value(b'PROVIDE_INFORMED_ANALYSIS', 2, b'Provide Informed Analysis', common.enums.WritingGoal)), (3, django_enumfield.enum.Value(b'BUILD_THOUGHT_LEADERSHIP', 3, b'Build Thought Leadership', common.enums.WritingGoal)), (4, django_enumfield.enum.Value(b'REPURPOSE_EXISTING_WRITING', 4, b'Repurpose Existing Writing', common.enums.WritingGoal)), (5, django_enumfield.enum.Value(b'PROMOTE_TOPIC', 5, b'Promote Topic', common.enums.WritingGoal)), (6, django_enumfield.enum.Value(b'EDUCATE_INSTRUCT', 6, b'Eduate Instruct', common.enums.WritingGoal))]),
        ),
        migrations.AddField(
            model_name='writingtaskmeta',
            name='point_of_view',
            field=models.PositiveIntegerField(blank=True, null=True, choices=[(1, django_enumfield.enum.Value(b'FIRST_PERSON', 1, b'1st Person', common.enums.WritingPointOfView)), (2, django_enumfield.enum.Value(b'SECOND_PERSON', 2, b'2nd Person', common.enums.WritingPointOfView)), (3, django_enumfield.enum.Value(b'THIRD_PERSON', 3, b'3rd Person', common.enums.WritingPointOfView))]),
        ),
        migrations.AddField(
            model_name='writingtaskmeta',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='writingtaskmeta',
            name='style',
            field=models.PositiveIntegerField(blank=True, null=True, choices=[(1, django_enumfield.enum.Value(b'AUTHORATIATIVE', 1, b'Authoratiative', common.enums.WritingStyle)), (2, django_enumfield.enum.Value(b'FORMAL', 2, b'Formal', common.enums.WritingStyle)), (3, django_enumfield.enum.Value(b'INSTRUCTIONAL', 3, b'Instructional', common.enums.WritingStyle)), (4, django_enumfield.enum.Value(b'VIRAL', 4, b'Viral', common.enums.WritingStyle)), (5, django_enumfield.enum.Value(b'CASUAL', 5, b'Casual', common.enums.WritingStyle)), (6, django_enumfield.enum.Value(b'WITTY', 6, b'Witty', common.enums.WritingStyle))]),
        ),
        migrations.AddField(
            model_name='writingtaskmeta',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, django_enumfield.enum.Value(b'SHORT_BLOG_POST', 1, b'Short Blog Post', common.enums.WritingContentType)), (2, django_enumfield.enum.Value(b'LONG_BLOG_POST', 2, b'Long Blog Post', common.enums.WritingContentType)), (3, django_enumfield.enum.Value(b'WEBSITE_PAGE', 3, b'Website Page', common.enums.WritingContentType)), (4, django_enumfield.enum.Value(b'ARTICLE', 4, b'Article', common.enums.WritingContentType)), (5, django_enumfield.enum.Value(b'PRESS_RELEASE', 5, b'Press Release', common.enums.WritingContentType))]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, django_enumfield.enum.Value(b'INACTIVE', 1, b'Inactive', common.enums.TaskStatus)), (2, django_enumfield.enum.Value(b'ACTIVE', 2, b'Active', common.enums.TaskStatus)), (3, django_enumfield.enum.Value(b'FINISHED', 3, b'Finished', common.enums.TaskStatus))]),
        ),
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, django_enumfield.enum.Value(b'SHORT_BLOG_POST', 1, b'Short Blog Post', common.enums.WritingContentType)), (2, django_enumfield.enum.Value(b'LONG_BLOG_POST', 2, b'Long Blog Post', common.enums.WritingContentType)), (3, django_enumfield.enum.Value(b'WEBSITE_PAGE', 3, b'Website Page', common.enums.WritingContentType)), (4, django_enumfield.enum.Value(b'ARTICLE', 4, b'Article', common.enums.WritingContentType)), (5, django_enumfield.enum.Value(b'PRESS_RELEASE', 5, b'Press Release', common.enums.WritingContentType))]),
        ),
    ]
