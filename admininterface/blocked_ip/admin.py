from django.contrib import admin
from .models import BlockedIp
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
# Register your models here.


class BlockedIpAdmin(admin.ModelAdmin) :
    search_fields = ['client_ip', 'block_start', 'force_remove', ]
    list_display = ['client_ip', 'block_start', 'force_remove']

    def has_delete_permission(self, request, obj=None):
        return False

    class Meta:
        model = BlockedIp

admin.site.register(BlockedIp, BlockedIpAdmin)
admin.site.unregister(User)
admin.site.unregister(Group)
