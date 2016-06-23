# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_auto_20160622_0219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Excuse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=b'I will not be attending because', verbose_name=b'Reasoning')),
                ('response_message', models.TextField(default=b'Your excuse was not approved because')),
                ('status', models.CharField(default=b'0', max_length=1, choices=[(b'0', b'Pending'), (b'1', b'Approved'), (b'2', b'Denied')])),
                ('brother', models.ForeignKey(to='dashboard.Brother')),
                ('event', models.ForeignKey(to='dashboard.ChapterEvent')),
                ('semester', models.ForeignKey(blank=True, to='dashboard.Semester', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudyTableEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('attendees', models.ManyToManyField(to='dashboard.Brother')),
                ('semester', models.ForeignKey(blank=True, to='dashboard.Semester', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='eventexcuse',
            name='brother',
        ),
        migrations.RemoveField(
            model_name='eventexcuse',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventexcuse',
            name='semester',
        ),
        migrations.DeleteModel(
            name='EventExcuse',
        ),
    ]
