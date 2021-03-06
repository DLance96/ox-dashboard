# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-06-21 13:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_auto_20160621_0515'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(choices=[(b'0', b'Fall'), (b'1', b'Spring'), (b'2', b'Summer')], default=b'0', max_length=1)),
                ('year', models.IntegerField(choices=[(2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016)], default=2016)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=b'Service Event', max_length=200)),
                ('description', models.TextField(default=b'I did the service thing')),
                ('hours', models.IntegerField(default=0)),
                ('submitted', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('brother', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Brother')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Semester')),
            ],
        ),
        migrations.RemoveField(
            model_name='serviceevent',
            name='brother',
        ),
        migrations.DeleteModel(
            name='ServiceEvent',
        ),
        migrations.AddField(
            model_name='brother',
            name='semester_joined',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Semester'),
        ),
        migrations.AddField(
            model_name='chapterevent',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Semester'),
        ),
        migrations.AddField(
            model_name='eventexcuse',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Semester'),
        ),
    ]
