# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_auto_20160622_0145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='semester_joined',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
        migrations.AlterField(
            model_name='chapterevent',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
        migrations.AlterField(
            model_name='eventexcuse',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
        migrations.AlterField(
            model_name='philanthropyevent',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='brother',
            field=models.ForeignKey(blank=True, to='dashboard.Brother', null=True),
        ),
        migrations.AlterField(
            model_name='potentialnewmember',
            name='last_name',
            field=models.CharField(max_length=45, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='potentialnewmember',
            name='secondary_contact',
            field=models.ForeignKey(related_name='secondary', blank=True, to='dashboard.Brother', null=True),
        ),
        migrations.AlterField(
            model_name='potentialnewmember',
            name='tertiary_contact',
            field=models.ForeignKey(related_name='tertiary', blank=True, to='dashboard.Brother', null=True),
        ),
        migrations.AlterField(
            model_name='recruitmentevent',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
        migrations.AlterField(
            model_name='serviceevent',
            name='semester',
            field=models.ForeignKey(blank=True, to='dashboard.Semester', null=True),
        ),
    ]
