# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-06-19 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brother',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('case_id', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('birthday', models.DateField()),
                ('school_status', models.CharField(choices=[(b'FR', b'Freshman'), (b'SO', b'Sophomore'), (b'JR', b'Junior'), (b'SR', b'Senior'), (b'FY', b'Fifth Year'), (b'AL', b'Alumni')], default=b'FR', max_length=2)),
            ],
        ),
    ]
