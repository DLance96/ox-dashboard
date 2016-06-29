# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0035_auto_20160627_1839'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommitteeMeetingEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(max_length=200)),
            ],
        ),
        migrations.RenameField(
            model_name='brother',
            old_name='current_residence',
            new_name='address',
        ),
        migrations.AlterField(
            model_name='brother',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='committeemeetingevent',
            name='attendees',
            field=models.ManyToManyField(to='dashboard.Brother', blank=True),
        ),
        migrations.AddField(
            model_name='committeemeetingevent',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
    ]
