from django.conf.urls import url

from . import views

# Create your urls here.

urlpatterns = [
    url(
        regex=r'^$',
        view=views.get_user_groups,
        name='group_list',
    ),
    url(
        regex=r'^(?P<group_id>\d+)/$',
        view=views.get_group_detail,
        name='group_detail',
    ),
    url(
        regex=r'^(?P<group_id>\d+)/members/$',
        view=views.list_group_members,
        name='group_members',
    ),
    url(
        regex=r'^create/$',
        view=views.create_group,
        name='group_create',
    ),
    url(
        regex=r'^join/(?P<group_id>\d+)/$',
        view=views.join_group,
        name='group_join',
    ),
    url(
        regex=r'^remove/(?P<group_id>\d+)/$',
        view=views.remove_group,
        name='group_remove',
    ),
    url(
        regex=r'^join/(?P<group_id>\d+)/request/$',
        view=views.send_group_membership_request,
        name='membership_request',
    ),
]
