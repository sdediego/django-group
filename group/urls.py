from django.conf.urls import url

from . import views

# Create your urls here.

urlpatterns = [
    url(
        regex=r'^$',
        view=views.getUserGroups,
        name='group_list',
    ),
    url(
        regex=r'^(?P<group_id>\d+)/$',
        view=views.getGroupDetail,
        name='group_detail',
    ),
    url(
        regex=r'^(?P<group_id>\d+)/members/$',
        view=views.listGroupMembers,
        name='group_members',
    ),
    url(
        regex=r'^create/$',
        view=views.createGroup,
        name='group_create',
    ),
    url(
        regex=r'^join/(?P<group_id>\d+)/$',
        view=views.joinGroup,
        name='group_join',
    ),
    url(
        regex=r'^remove/(?P<group_id>\d+)/$',
        view=views.removeGroup,
        name='group_remove',
    ),
    url(
        regex=r'^join/(?P<group_id>\d+)/request/$',
        view=views.sendGroupMembershipRequest,
        name='membership_request',
    ),
]
