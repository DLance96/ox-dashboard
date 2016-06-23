# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_auto_20160622_0213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='case_ID',
            field=models.CharField(max_length=10),
        ),
    ]
