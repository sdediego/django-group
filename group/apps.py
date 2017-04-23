from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from .signals import (group_created, group_removed, group_and_membership_remove,
                      membership_request_accepted, membership_request_rejected,
                      membership_request_viewed, membership_request_sent,
                      membership_created, membership_removed)
from .signals import (create_group_admin, remove_group_and_memberships)

# Define your app configuration here.

class GroupConfig(AppConfig):
    name = 'group'
    label = 'group'
    verbose_name = _('Group')

    def ready(self):
        """
        Connect signal receivers or import signals module.
        """
        from apps.group.models import Group
        group_created.connect(receiver=create_group_admin, sender=Group)
        group_and_membership_remove.connect(receiver=remove_group_and_memberships, sender=Group)
