# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-06-19 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20160619_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventexcuse',
            name='description',
            field=models.TextField(default=b'I will not be attending None because', verbose_name=b'Reasoning'),
        ),
    ]