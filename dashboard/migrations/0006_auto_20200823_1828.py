# Generated by Django 3.0.7 on 2020-08-23 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20200823_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(choices=[('2', 'Scholarship'), ('3', 'Unassigned'), ('0', 'Alumni Relations'), ('1', 'Membership Development')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(choices=[('4', 'Unassigned'), ('0', 'Recruitment'), ('2', 'Health and Safety'), ('3', 'Social'), ('1', 'Public Relations')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('0', 'Recruitment'), ('5', 'Membership Development'), ('6', 'Scholarship'), ('2', 'Health and Safety'), ('3', 'Social'), ('1', 'Public Relations'), ('4', 'Alumni Relations')], max_length=1),
        ),
    ]