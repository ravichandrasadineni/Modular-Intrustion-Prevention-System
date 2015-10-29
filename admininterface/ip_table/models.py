from django.db import models

# Create your models here.

class IpTable(models.Model):
    client_ip = models.CharField(max_length=19, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    block_start = models.DateTimeField(blank=True, null=True)
    force_remove = models.NullBooleanField()
    count = models.IntegerField()
    class Meta:
        db_table = 'ip_table'

    def __unicode__(self):
        return self.client_ip

