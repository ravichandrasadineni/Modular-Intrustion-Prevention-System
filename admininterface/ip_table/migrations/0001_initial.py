# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IpTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_ip', models.CharField(max_length=19, null=True, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('block_start', models.DateTimeField(null=True, blank=True)),
                ('force_remove', models.NullBooleanField()),
                ('count', models.IntegerField()),
            ],
            options={
                'db_table': 'ip_table',
            },
        ),
    ]
