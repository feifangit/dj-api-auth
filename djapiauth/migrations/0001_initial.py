# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import djapiauth.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIEntryPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('pattern', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Entry point',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='APIKeys',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('apikey', models.CharField(default=djapiauth.models.gen_apikey, unique=True, max_length=50)),
                ('seckey', models.CharField(default=djapiauth.models.gen_seckey, max_length=50)),
                ('note', models.CharField(max_length=80, null=True, blank=True)),
                ('apis', models.ManyToManyField(help_text=b'accessible api entries', to='djapiauth.APIEntryPoint', null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Credential',
            },
            bases=(models.Model,),
        ),
    ]
