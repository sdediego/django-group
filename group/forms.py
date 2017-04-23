from django import forms

from .models import Group, GroupMembership, GroupMembershipRequest

# Create your forms here.

class GroupCreationForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = [
            'name',
            'access',
        ]
        labels = {
            'name': 'Group name',
            'access': 'Type of access',
        }
        widgets = {
            'name': forms.TextInput(),
            'access': forms.TextInput(),
        }

    def save(self, *args, **kwargs):
        """
        Save new created group and assign the
        administrator permit to the user who
        created it.
        """
        user = kwargs.get('request').user
        if user.is_authenticated():
            name = self.cleaned_data.get('name')
            access = self.cleaned_data.get('access')
            group, administrator = Group.objects.create_new_group(user= user, name=name, access=access)
            return group, administrator
        return False


class GroupMembershipRequestForm(forms.ModelForm):

    class Meta:
        model = GroupMembershipRequest
        fields = [
            'message',
        ]
        labels = {
            'message': 'Message',
        }
        widgets = {
            'message': forms.Textarea(),
        }

    def save(self, *args, **kwargs):
        """
        Save membership request to the private
        group administrator.
        """
        user = kwargs.get('user')
        if user.is_authenticated():
            group = kwargs.get('group')
            admin = GroupMembership.objects.get_group_admin(group=group)
            msg = self.cleaned_data.get('message')
            request = GroupMembershipRequest.objects.send_membership_request(
                        from_user=user, to_admin=admin, group=group, message=msg)
            return request
        return False
