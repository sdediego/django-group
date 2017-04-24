# Copyright (c) 2016 Publisher, Inc. - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
# Written by Sergio de Diego <sergio.dediego@outlook.com>, October 2016.

from functools import wraps

# Create your decorators here.

def group_admin_permit_required(method):
    @wraps(method)
    def method_wrapper(self, user, group, *args, **kwargs):
        if callable(getattr(self, method.__name__, None)):
            if user.is_authenticated():
                from apps.group.models import GroupMembership
                admin = GroupMembership.objects.get_group_admin(group)
                if user == self.to_administrator and user == admin:
                    return method(self, user, group, *args, **kwargs)
        return False
    return method_wrapper
