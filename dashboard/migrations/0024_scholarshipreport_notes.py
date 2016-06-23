# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_auto_20160622_0438'),
    ]

    operations = [
        migrations.AddField(
            model_name='scholarshipreport',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
