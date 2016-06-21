# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20160621_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhilanthropyEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Philanthropy Event', max_length=200)),
                ('date_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PotentialNewMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\+?1?\\d{9,15}$', message=b"Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])),
            ],
        ),
        migrations.CreateModel(
            name='RecruitmentEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Recruitment Event', max_length=200)),
                ('date_time', models.DateTimeField()),
                ('attendees', models.ManyToManyField(to='dashboard.PotentialNewMember')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Service Event', max_length=200)),
                ('date_time', models.DateTimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='chapterevent',
            name='event_type',
        ),
        migrations.AlterField(
            model_name='brother',
            name='first_name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='brother',
            name='last_name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='semester',
            name='season',
            field=models.CharField(default=b'0', max_length=1, choices=[(b'0', b'Spring'), (b'1', b'Summer'), (b'2', b'Fall')]),
        ),
        migrations.AddField(
            model_name='serviceevent',
            name='rsvp_brothers',
            field=models.ManyToManyField(to='dashboard.Brother'),
        ),
        migrations.AddField(
            model_name='serviceevent',
            name='semester',
            field=models.ForeignKey(to='dashboard.Semester', null=True),
        ),
        migrations.AddField(
            model_name='recruitmentevent',
            name='semester',
            field=models.ForeignKey(to='dashboard.Semester', null=True),
        ),
        migrations.AddField(
            model_name='potentialnewmember',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary', to='dashboard.Brother'),
        ),
        migrations.AddField(
            model_name='potentialnewmember',
            name='secondary_contact',
            field=models.ForeignKey(related_name='secondary', to='dashboard.Brother', null=True),
        ),
        migrations.AddField(
            model_name='potentialnewmember',
            name='tertiary_contact',
            field=models.ForeignKey(related_name='tertiary', to='dashboard.Brother', null=True),
        ),
        migrations.AddField(
            model_name='philanthropyevent',
            name='rsvp_brothers',
            field=models.ManyToManyField(to='dashboard.Brother'),
        ),
        migrations.AddField(
            model_name='philanthropyevent',
            name='semester',
            field=models.ForeignKey(to='dashboard.Semester', null=True),
        ),
    ]
