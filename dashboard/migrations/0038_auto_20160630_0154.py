# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-06-30 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0037_auto_20160628_2150'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recruitmentevent',
            old_name='attendees',
            new_name='attendees_pnms',
        ),
        migrations.AddField(
            model_name='recruitmentevent',
            name='attendees_brothers',
            field=models.ManyToManyField(blank=True, to='dashboard.Brother'),
        ),
        migrations.AddField(
            model_name='recruitmentevent',
            name='rush',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='serviceevent',
            name='attendees',
            field=models.ManyToManyField(blank=True, related_name='attended', to='dashboard.Brother'),
        ),
        migrations.AlterField(
            model_name='serviceevent',
            name='rsvp_brothers',
            field=models.ManyToManyField(blank=True, related_name='rsvp', to='dashboard.Brother'),
        ),
    ]