from functools import wraps

# Create your decorators here.

def group_admin_permit_required(method):
    @wraps(method)
    def method_wrapper(self, user, group, *args, **kwargs):
        if user.is_authenticated():
            from apps.group.models import GroupMembership
            admin = GroupMembership.objects.get_group_admin(group)
            if user == self.to_administrator and user == admin:
                return method(self, user, group, *args, **kwargs)
        return False
    return method_wrapper
