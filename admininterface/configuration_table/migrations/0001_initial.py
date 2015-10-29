# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurationsTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_duration', models.IntegerField()),
                ('threshold_retries', models.IntegerField()),
                ('block_time', models.IntegerField()),
            ],
            options={
                'db_table': 'ip_table',
            },
        ),
    ]
