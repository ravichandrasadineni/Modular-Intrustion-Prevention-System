from django.contrib import admin
from .models import ConfigurationsTable
# Register your models here.


class ConfigurationTableAdmin(admin.ModelAdmin) :
    search_fields = ['time_duration', 'threshold_retries', 'block_time']
    list_display = ['time_duration', 'threshold_retries', 'block_time']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    class Meta:
        model = ConfigurationsTable
admin.site.register(ConfigurationsTable, ConfigurationTableAdmin)