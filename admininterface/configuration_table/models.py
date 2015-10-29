from django.db import models

# Create your models here.

class ConfigurationsTable(models.Model):
    time_duration = models.IntegerField()
    threshold_retries = models.IntegerField()
    block_time = models.IntegerField()

    class Meta:
        db_table = 'configuration_table'

