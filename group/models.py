# Copyright (c) 2016 Publisher, Inc. - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
# Written by Sergio de Diego <sergio.dediego@outlook.com>, October 2016.

import datetime

from django.contrib.auth.models import User
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.group.caches import cache_bust
from apps.group.decorators import group_admin_permit_required
from apps.group.managers import GroupManager, GroupMembershipManager, GroupMembershipRequestManager

# Create your models here.

GROUP_ACCESS = (
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Private'),
)

PERMIT_TYPES = (
    ('ADMIN', 'Administrator'),
    ('PART', 'Participant'),
)


class Group(models.Model):
    """
    Model to define groups.
    Each group can contain any number of members and
    any user can be member of as many groups as desired.
    """
    name = models.CharField(
        _('Name'),
        max_length=100,
        blank=False,
    )
    access = models.CharField(
        _('Access'),
        max_length=7,
        blank=False,
        choices=GROUP_ACCESS,
    )
    members = models.ManyToManyField(
        User,
        through='GroupMembership',
    )
    created = models.DateField(
        _('Date'),
        default=datetime.date.today,
        editable=False,
    )

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    objects = GroupManager()

    def __str__(self):
        return 'Group {name}'.format(name=self.name)

    def get_absolute_url(self, group):
        """
        Calculate the canonical URL for an object to return a string
        that can be used to refer to the object over HTTP.
        """
        reverse_url = reverse('group:group_detail', kwargs={'group_id': self.pk})
        return reverse_url

    @transaction.atomic
    def remove_group(self, user):
        """
        Remove selected group by its administrator.
        """
        group_pk = self.pk
        response = group_and_membership_remove.send(sender=self.__class__, user=user, group=self)
        receiver, deleted = response[0]
        if deleted:
            cache_bust([('groups', user.pk), ('memberships', group_pk)])
            return True
        return False


class GroupMembership(models.Model):
    """
    Model to define each member of a group.
    """
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )
    permit = models.CharField(
        _('Permit'),
        max_length=5,
        blank=False,
        choices=PERMIT_TYPES,
    )
    date_joined = models.DateField(
        _('Date'),
        default=datetime.date.today,
        editable=False,
    )

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')

    objects = GroupMembershipManager()

    def __str__(self):
        return '{user} is member of the group {group}'.format(user=self.member.username, group=self.group.name)

    @transaction.atomic
    def remove_membership(self, user):
        """
        Delete user's membership to a group.
        User can leave the group or be removed by the
        group administrator.
        If the administrator leaves the group the group
        is deleted.
        """
        if user.is_authenticated() and self.objects.is_member(user):
            administrator = self.objects.get_group_admin(self.group)
            if user == self.member != administrator or user == administrator:
                group = self.group
                self.delete()
                cache_bust([('groups', user.pk), ('memberships', group.pk)])
                return True
            elif user == self.member == administrator:
                response = Group.objects.remove_group(user)
                return response
        return False


class GroupMembershipRequest(models.Model):
    """
    Model to define a membership request to join a
    public/private group.
    """
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='from_user',
    )
    to_administrator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_administrator',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )
    message = models.TextField(
        _('Message'),
        max_length=150,
        blank=True,
        default='I would like to join the group.',
        help_text=_('Write custom message to group administrator.'),
        error_messages={
            'invalid': _('Insert text up to 150 characters.')
        },
    )
    created = models.DateTimeField(
        _('Created'),
        default=timezone.now,
        editable=False,
    )
    rejected = models.DateTimeField(
        _('Rejectd'),
        blank=True,
        null=True,
        editable=True)
    viewed = models.DateTimeField(
        _('Viewed'),
        blank=True,
        null=True,
        editable=True,
    )

    class Meta:
        verbose_name = _('Membership Request')
        verbose_name_plural = _('Membership Requests')

    objects = GroupMembershipRequestManager()

    def __str__(self):
        return '{user} membership request to {group}'.format(user=self.from_user, group=self.group)

    @group_admin_permit_required
    @transaction.atomic
    def accept_membership_request(self, user, group):
        """
        The administrator of the group accepts
        the request to join the group.
        """
        #if user.is_authenticated() and user == self.to_administrator:
        membership, created = GroupMembership.objects.get_or_create(member=self.from_user, group=self.group, permit='PART')
        if created:
            self.remove_membership_request(user)
            membership_request_accepted.send(sender=self.__class__, user=self.from_user, request=self)
            cache_bust([('memberships', group.pk)])
            return membership

    @group_admin_permit_required
    @transaction.atomic
    def reject_membership_request(self, user, group):
        """
        The administrator of the group rejects
        the request to join the group.
        """
        #if user.is_authenticated() and user == self.to_administrator:
        if not self.rejected:
            self.rejected = timezone.now()
            self.save()
            membership_request_rejectd.send(sender=self.__class__, user=self.from_user, request=self)
            cache_bust([('requests', self.to_administrator.pk)])
            return True

    @group_admin_permit_required
    @transaction.atomic
    def remove_membership_request(self, user, group):
        """
        The administrator of the group removes
        the request to join the group.
        """
        #if user.is_authenticated() and user == self.to_administrator:
        self.delete()
        cache_bust([('requests', self.to_administrator.pk)])
        return True

    @transaction.atomic
    def remove_sent_request(self, user):
        """
        The administrator of the group removes
        the request to join the group.
        """
        if user.is_authenticated() and user == self.from_user:
            self.delete()
            cache_bust([('sent_requests', user.pk)])
            return True
        return False

    @group_admin_permit_required
    @transaction.atomic
    def mark_viewed_membership_request(self, user, group):
        """
        The membership request if marked as viewed
        the first time administrator reads it.
        Also can be manually marked and unmark as viewed.
        """
        #if user.is_authenticated() and user == self.to_administrator:
        if not self.viewed:
            self.viewed = timezone.now()
            self.saved()
            membership_request_viewed.send(sender=self.__class__, user=self.from_user, request=self)
            cache_bust([('requests', self.to_administrator.pk)])
            return True

    @group_admin_permit_required
    @transaction.atomic
    def unmark_viewed_membership_request(self, user, group):
        """
        The administrator can be manually unmark
        as viewed the membership request.
        """
        #if user.is_authenticated() and user == self.to_administrator:
        if self.viewed:
            self.viewed =''
            self.saved()
            cache_bust([('requests', self.to_administrator.pk)])
            return True
