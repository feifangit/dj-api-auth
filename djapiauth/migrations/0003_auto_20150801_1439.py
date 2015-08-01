# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djapiauth', '0002_apikeys_apitree'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apientrypoint',
            name='pattern',
            field=models.CharField(max_length=300),
            preserve_default=True,
        ),
    ]
