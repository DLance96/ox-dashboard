# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='brother',
            field=models.ForeignKey(to='dashboard.Brother', null=True),
        ),
    ]
