#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_security import current_user
from flask import request

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
    - Create action given to owners only.
    - Read access given to everyone if public, according to a record ownership if not.
    - Update access given to record owners.
    - Delete access given to record owners.
    """

    create_actions = ['create']
    read_actions = ['read']
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


def has_create_permission(user, record):
    """Check if user is authenticated and has create access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        search = request._methodview.search_class()
        mapping = search.get_mapping(str(record.index))
        # set.isdisjoint() is faster than set.intersection()
        create_access_groups = mapping['_meta']['_owner']
        if user_provides and not set(user_provides).isdisjoint(set(create_access_groups)):
            return True
    return False


def has_update_permission(user, record):
    """Check if user is authenticated and has update access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        update_access_groups = record['_access']['update']
        if user_provides and not set(user_provides).isdisjoint(set(update_access_groups)):
            return True
    return False


def has_read_record_permission(user, record):
    """Check if user is authenticated and has read access. This implies reading one document"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        read_access_groups = record['_access']['read']
        if user_provides and not set(user_provides).isdisjoint(set(read_access_groups)):
            return True
    return False


def has_delete_permission(user, record):
    """Check if user is authenticated and has delete access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        delete_access_groups = record['_access']['delete']
        if user_provides and not set(user_provides).isdisjoint(set(delete_access_groups)):
            return True
    return False


# Utility functions


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


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]
