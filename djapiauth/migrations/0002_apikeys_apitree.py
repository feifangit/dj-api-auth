# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djapiauth.models


class Migration(migrations.Migration):

    dependencies = [
        ('djapiauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikeys',
            name='apitree',
            field=models.TextField(default=djapiauth.models.gen_empty_list),
            preserve_default=True,
        ),
    ]
