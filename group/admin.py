from django.contrib import admin

from .models import Group, GroupMembership, GroupMembershipRequest

# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    model = Group
    raw_id_fields = ('members',)


class GroupMembershipAdmin(admin.ModelAdmin):
    model = GroupMembership
    raw_id_fields = ('member', 'group')


class GroupMembershipRequestAdmin(admin.ModelAdmin):
    model = GroupMembershipRequest
    raw_id_fields = ('from_user', 'to_administrator', 'group')


admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMembership, GroupMembershipAdmin)
admin.site.register(GroupMembershipRequest, GroupMembershipRequestAdmin)
