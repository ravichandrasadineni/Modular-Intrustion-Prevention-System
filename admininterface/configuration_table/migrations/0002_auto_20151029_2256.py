# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configuration_table', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='configurationstable',
            table='configuration_table',
        ),
    ]
