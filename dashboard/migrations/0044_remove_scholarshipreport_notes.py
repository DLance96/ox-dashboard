# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-07-22 02:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0043_scholarshipreport_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scholarshipreport',
            name='notes',
        ),
    ]
