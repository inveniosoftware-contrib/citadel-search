#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_security import current_user
from flask_principal import ActionNeed
from invenio_access import DynamicPermission

from .utils import get_user_provides

"""Access control for CERN Search."""


def record_permission_factory(record=None, action=None):
    """Record permission factory."""
    return RecordPermission.create(record, action)


def record_create_permission_factory(record=None):
    """Create permission factory."""
    return record_permission_factory(record=record, action='create')


def record_read_permission_factory(record=None):
    """Read permission factory."""
    return record_permission_factory(record=record, action='read')


def record_update_permission_factory(record=None):
    """Update permission factory."""
    return record_permission_factory(record=record, action='update')


def record_delete_permission_factory(record=None):
    """Delete permission factory."""
    return record_permission_factory(record=record, action='delete')


class RecordPermission(object):
    """Record permission.
    - Create action given to admins only.
    - Read access given to everyone if public, according to a record if not.
    - Update access given to record owners.
    - Delete access given to admins only.
    """

    create_actions = ['create']
    read_actions = ['read']
    read_files_actions = ['read-files']
    read_eos_path_actions = ['read-eos-path']
    update_actions = ['update']
    delete_actions = ['delete']

    def __init__(self, record, func, user):
        """Initialize a file permission object."""
        self.record = record
        self.func = func
        self.user = user or current_user

    def can(self):
        """Determine access."""
        return self.func(self.user, self.record)

    @classmethod
    def create(cls, record, action, user=None):
        """Create a record permission."""
        # Allow everything for testing
        if action in cls.create_actions:
            return cls(record, allow, user)  # return cls(record, has_admin_permission, user)
        elif action in cls.read_actions:
            return cls(record, allow, user)  # return cls(record, has_read_record_permission, user)
        elif action in cls.update_actions:
            return cls(record, allow, user)  # return cls(record, has_update_permission, user)
        elif action in cls.delete_actions:
            return cls(record, allow, user)  # return cls(record, has_admin_permission, user)
        else:
            return cls(record, deny, user)


def has_read_record_permission(user, record):
    """Check if user has read access to the record."""
    # Allow everyone for public records
    if is_public(record, 'read'):
        return True

    # Allow e-group members
    user_provides = get_user_provides()
    read_access_groups = record['_access']['read']

    if not set(user_provides).isdisjoint(set(read_access_groups)):
        return True

    return has_admin_permission()


def has_update_permission(user, record):
    """Check if user has update access to the record."""
    user_id = int(user.get_id()) if user.is_authenticated else None

    # Allow owners
    deposit_creator = record.get('_deposit', {}).get('created_by', -1)
    if user_id == deposit_creator:
        return True

    # Allow based in the '_access' key
    user_provides = get_user_provides()
    # set.isdisjoint() is faster than set.intersection()
    allowed_users = record.get('_access', {}).get('update', [])
    if allowed_users and not set(user_provides).isdisjoint(set(allowed_users)):
        return True

    return has_admin_permission()


def has_admin_permission(user=None, record=None):
    """Check if user has admin access to record.
    This function has to accept 2 parameters (as all other has_foo_permissions,
    to allow for dynamic dispatch.
    """
    # Allow administrators
    # Taken from invenio_desposit.permissions.py due to incompatibilities in the ES version support
    return DynamicPermission(
        ActionNeed('index-admin-access')).can()  # TODO Update for invenio_access.permissions.Permission


#
# Utility functions
#
def deny(user, record):
    """Deny access."""
    return False


def allow(user, record):
    """Allow access."""
    return True


def is_public(data, action):
    """Check if the record is fully public.
    In practice this means that the record doesn't have the ``access`` key or
    the action is not inside access or is empty.
    """
    return '_access' not in data or not data.get('_access', {}).get(action)
