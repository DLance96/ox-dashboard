# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-12-31 00:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0059_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='sundaydetail',
            name='finished_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='thursdaydetail',
            name='finished_time',
            field=models.DateTimeField(null=True),
        ),
    ]
