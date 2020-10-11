# Generated by Django 3.0.7 on 2020-09-21 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_phonetreenode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='year',
            field=models.IntegerField(choices=[(2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025)], default=2020),
        ),
    ]