from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your exceptions here.

class GroupAdministratorError(IntegrityError):
    """
    Raise errors related to group administrator permissions.
    """
    pass


class GroupError(IntegrityError):
    """
    Raise errors related to group integrity.
    """
    pass


class GroupMembershipError(ValidationError):
    """
    Raise errors related to user group membership
    when a user is or not member of a group.
    """
    pass


class SendRequestError(ValidationError):
    """
    Raise error when trying to send a membership
    request to a group already sent.
    """
    pass
