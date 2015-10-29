from django.contrib import admin
from .models import IpTable
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
# Register your models here.


class IpTableAdmin(admin.ModelAdmin) :
    search_fields = ['client_ip', 'start_time', 'block_start', 'force_remove', 'count']
    list_display = ['client_ip', 'start_time', 'block_start', 'force_remove', 'count']
    #readonly_fields = ('client_ip', 'start_time', 'block_start', 'count')
    def has_delete_permission(self, request, obj=None):
        return False
    class Meta :
        model = IpTable

admin.site.register(IpTable, IpTableAdmin)
admin.site.unregister(User)
admin.site.unregister(Group)
