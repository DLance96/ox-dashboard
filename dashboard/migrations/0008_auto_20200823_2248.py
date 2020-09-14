# Generated by Django 3.0.7 on 2020-08-24 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20200823_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='minecraftphoto',
            name='name',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='name',
        ),
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(choices=[('3', 'Unassigned'), ('0', 'Alumni Relations'), ('1', 'Membership Development'), ('2', 'Scholarship')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(choices=[('0', 'Recruitment'), ('4', 'Unassigned'), ('2', 'Health and Safety'), ('3', 'Social'), ('1', 'Public Relations')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('4', 'Alumni Relations'), ('0', 'Recruitment'), ('2', 'Health and Safety'), ('5', 'Membership Development'), ('6', 'Scholarship'), ('3', 'Social'), ('1', 'Public Relations')], max_length=1),
        ),
    ]
