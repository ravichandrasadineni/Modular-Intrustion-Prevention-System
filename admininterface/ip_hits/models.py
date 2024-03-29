from django.db import models

# Create your models here.


class IpHits(models.Model):
    client_ip = models.CharField(max_length=19, blank=True, null=True)
    hit_time = models.DateTimeField(blank=True, null=True)
    appl_name = models.CharField(max_length=19, blank=True, null=True)
    class Meta:
        db_table = 'ip_hits'
