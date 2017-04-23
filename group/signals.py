from django.dispatch import Signal

# Create your signals here.

group_created = Signal(providing_args=['user', 'group'])
group_removed = Signal(providing_args=['user', 'group'])
group_and_membership_remove = Signal(providing_args=['group'])
membership_request_accepted = Signal()
membership_request_rejected = Signal()
membership_request_viewed = Signal()
membership_request_sent = Signal()
membership_created = Signal()
membership_removed = Signal()

# Create your receivers here.

def create_group_admin(sender, user, group, *args, **kwargs):
    """
    Add the user who created a new group with
    administrator permit. There can only be
    one administrator for each group.
    """
    from apps.group.models import GroupMembership
    administrator = GroupMembership.objects.set_group_admin(user=user, group=group)
    return administrator


def remove_group_and_memberships(sender, user, group, *args, **kwargs):
    """
    A group administrator removes the group.
    Also if an administrator leaves the group then
    the group itself is deleted.
    """
    from apps.group.models import Group, GroupMembership
    if user.is_authenticated() and user == GroupMembership.objects.get_group_admin(group):
        try:
            deleted = Group.objects.get(pk=group.pk).deleted()
            if deleted:
                GroupMembership.objects.filter(group=group).delete()
                return True
        except Group.DoesNotExist:
            raise GroupError('Group does not exit.')
    return False
