# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_auto_20160622_0205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='brother',
            field=models.ForeignKey(blank=True, to='dashboard.Brother', null=True),
        ),
    ]
