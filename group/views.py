from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import GroupCreationForm, GroupMembershipRequestForm
from .models import Group, GroupMembership

# Create your views here.

@login_required(login_url='/login/')
def create_group(request, template='group_create.html'):
    """
    Create a new group.
    The User who creates the group will became its administrator.
    """
    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group, admin = form.save(request=request)
            return redirect('group_detail', group_id=group.pk)
    form = GroupCreationForm()
    return render(request, template, {'form': form})


@login_required(login_url='/login/')
@require_http_methods(['GET'])
def get_group_detail(request, group_id, template='group_detail.html'):
    """
    Display group information.
    """
    group = Group.objects.get(pk=group_id)
    memberships, members = GroupMembership.objects.memberships(group__pk=group_id)
    return render(request, template, {'group': group, 'memberships': memberships,'members': members})


@login_required(login_url='/login/')
@require_http_methods(['GET'])
def get_user_groups(request, template='group_user_list.html'):
    """
    Display user groups list.
    """
    groups = Groups.objects.get_user_groups(user=request.user)
    return render(request, template, {'groups': groups})


@login_required(login_url='/login/')
def join_group(request, group_id):
    """
    User joins a group and becomes one of its members.
    If the group has public access user will be added as a member instantly,
    whereas if the group has private access the user should submit a joining
    request to the administrator for membership approval.
    """
    group = Group.objects.get(pk=group_id)
    redirect = GroupMembership.objects.add_membership(user=request.user, group=group)
    return redirect


@login_required(login_url='/login/')
@require_http_methods(['GET'])
def list_group_members(request, group_id, template='group_members.html'):
    """
    Get the list of group members.
    """
    return redirect(getGroupDetail, group_id=group_id, template=template)


@login_required(login_url='/login/')
def remove_group(request, group_id, template='group_remove.html'):
    """
    Remove a group.
    The group can be removed only by its administrator.
    """
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        group.remove_group(user=request.user)
        return redirect('group:group_list')
    return render(request, template, {'group': group})


@login_required(login_url='/login/')
def send_group_membership_request(request, group_id, template='group_send_request.html'):
    """
    Send membership request to the administrator
    of a private group.
    """
    if request.method == 'POST':
        form = GroupMembershipRequestForm(request.POST)
        if form.is_valid():
            group = Group.objects.get(pk=group_id)
            form.save(user=request.user, group=group)
            return redirect('group:group_list')
    form = GroupMembershipRequestForm()
    return render(request, template, {'form': form})
