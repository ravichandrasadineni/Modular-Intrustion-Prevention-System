from django.db import models

# Create your models here.


class BlockedIp(models.Model):
    client_ip = models.CharField(max_length=19, blank=True, null=True)
    block_start = models.DateTimeField(blank=True, null=True)
    force_remove = models.NullBooleanField()

    class Meta:
        db_table = 'blocked_ip'

    def __unicode__(self):
        return self.client_ip

