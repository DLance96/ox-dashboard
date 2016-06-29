# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0036_auto_20160628_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='committeemeetingevent',
            name='type',
        ),
        migrations.AddField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(default='1', max_length=1, choices=[(b'3', b'Social'), (b'6', b'Scholarship'), (b'5', b'Membership Development'), (b'1', b'Public Relations'), (b'2', b'Health and Safety'), (b'4', b'Alumni Relations'), (b'0', b'Recruitment')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='brother',
            name='brother_status',
            field=models.CharField(default=b'0', max_length=1, choices=[(b'0', b'Candidate'), (b'1', b'Brother'), (b'2', b'Alumni')]),
        ),
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(default=b'3', max_length=1, choices=[(b'2', b'Scholarship'), (b'1', b'Membership Development'), (b'3', b'Unassigned'), (b'0', b'Alumni Relations')]),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(default=b'4', max_length=1, choices=[(b'3', b'Social'), (b'2', b'Health and Safety'), (b'1', b'Public Relations'), (b'0', b'Recruitment'), (b'4', b'Unassigned')]),
        ),
    ]
