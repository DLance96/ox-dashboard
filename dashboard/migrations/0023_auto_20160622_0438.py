# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_auto_20160622_0418'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScholarshipReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_semester_gpa', models.DecimalField(default=4.0, max_digits=5, decimal_places=2)),
                ('cumulative_gpa', models.DecimalField(default=4.0, max_digits=5, decimal_places=2)),
                ('scholarship_plan', models.TextField(default=b'Scholarship plan has not been setup yet if you past semester GPA or cum GPA are below 3.0 you should setup a meeting to have this corrected')),
            ],
        ),
        migrations.RemoveField(
            model_name='brother',
            name='cumulative_gpa',
        ),
        migrations.RemoveField(
            model_name='brother',
            name='past_semester_gpa',
        ),
        migrations.RemoveField(
            model_name='brother',
            name='scholarship_plan',
        ),
        migrations.AddField(
            model_name='chapterevent',
            name='minutes',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='chapterevent',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='philanthropyevent',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='recruitmentevent',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='serviceevent',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='scholarshipreport',
            name='brother',
            field=models.ForeignKey(to='dashboard.Brother'),
        ),
        migrations.AddField(
            model_name='scholarshipreport',
            name='semester',
            field=models.ForeignKey(to='dashboard.Semester'),
        ),
    ]
