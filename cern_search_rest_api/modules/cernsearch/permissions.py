#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from cern_search_rest_api.modules.cernsearch.utils import get_user_provides
from flask import current_app
from flask_security import current_user
from functools import partial

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


def record_list_permission_factory(record=None):
    """Read permission factory."""
    return record_permission_factory(record=record, action='list')


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
    list_actions = ['list']
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
        if action in cls.list_actions:
            return cls(record, has_list_permission, user)
        elif action in cls.create_actions:
            return cls(record, has_owner_permission, user)
        elif action in cls.read_actions:
            return cls(record, has_read_record_permission, user)
        elif action in cls.update_actions:
            return cls(record, has_update_permission, user)
        elif action in cls.delete_actions:
            return cls(record, has_delete_permission, user)
        else:
            return cls(record, deny, user)


def _granted(provides, needs):
    return provides and not set(provides).isdisjoint(set(needs))


def _user_granted(needs):
    return _granted(provides=get_user_provides(), needs=needs)


def has_owner_permission(user, record=None):
    """Check if user is authenticated and has create access"""
    log_action(user, 'CREATE/OWNER')

    # First authentication phase, decorator level
    if not record:
        return user.is_authenticated
    # Second authentication phase, record level
    if user.is_authenticated:
        admin_access = current_app.config.get('ADMIN_ACCESS_GROUPS', '')
        admin_access = admin_access.split(',')

        return _user_granted(admin_access)

    return False


def has_list_permission(user, record=None):
    """Check if user is authenticated and has create access"""
    if user:
        log_action(user, 'LIST')
        return user.is_authenticated
    else:
        return False


def has_update_permission(user, record):
    """Check if user is authenticated and has update access."""
    log_action(user, 'UPDATE')
    if user.is_authenticated:
        # Allow based in the '_access' key
        update_access = get_access_set(record['_access'], 'update')
        delete_access = get_access_set(record['_access'], 'delete')
        owner_access = get_access_set(record['_access'], 'owner')

        # The user is owner of the collection/schema
        # The user belongs to any access group, meaning the list is disjoint
        # Then grant access
        if has_owner_permission(user, record) or (
            _user_granted(update_access) or
            _user_granted(delete_access) or
            _user_granted(owner_access)
        ):
            current_app.logger.debug('Group sets not disjoint, user allowed')
            return True
    return False


def has_read_record_permission(user, record):
    """Check if user is authenticated and has read access. This implies reading one document."""
    log_action(user, 'READ')
    if user.is_authenticated:
        # Allow based in the '_access' key
        read_access = get_access_set(record['_access'], 'read')
        update_access = get_access_set(record['_access'], 'update')
        delete_access = get_access_set(record['_access'], 'delete')
        owner_access = get_access_set(record['_access'], 'owner')

        if not read_access:
            return True

        # The user is owner of the collection/schema
        # The user belongs to any access group, meaning the list is disjoint
        # Then grant access
        if has_owner_permission(user, record) or (
            _user_granted(read_access) or
            _user_granted(update_access) or
            _user_granted(delete_access) or
            _user_granted(owner_access)
        ):
            current_app.logger.debug('Group sets not disjoint, user allowed')
            return True
    return False


def has_delete_permission(user, record):
    """Check if user is authenticated and has delete access."""
    log_action(user, 'DELETE')
    if user.is_authenticated:
        # Allow based in the '_access' key
        delete_access = get_access_set(record['_access'], 'delete')
        owner_access = get_access_set(record['_access'], 'owner')

        # The user is owner of the collection/schema
        # The user belongs to any access group, meaning the list is disjoint
        # Then grant access
        if has_owner_permission(user, record) or (
            _user_granted(delete_access) or
            _user_granted(owner_access)
        ):
            current_app.logger.debug('Group sets not disjoint, user allowed')
            return True
    return False


"""Access control for CERN Search Admin Web UI."""


def admin_permission_factory(view):
    """Record permission factory."""
    return AdminPermission.create(view=view)


class AdminPermission(object):

    def __init__(self, func, user, view):
        """Initialize a file permission object."""
        self.user = user or current_user
        self.func = func
        self.view = view

    def can(self):
        """Determine access."""
        return self.func(self.user)

    @classmethod
    def create(cls, user=None, view=None):
        """Create a record permission."""
        # Allow everything for testing
        return cls(has_admin_view_permission, user, view)


def has_admin_view_permission(user):
    admin_access_groups = current_app.config['ADMIN_VIEW_ACCESS_GROUPS']
    if user.is_authenticated and admin_access_groups:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        admin_access_groups = admin_access_groups.split(',')
        if user_provides and not set(user_provides).isdisjoint(set(admin_access_groups)):
            current_app.logger.debug('User has admin view access')
            return True
    return False


# Utility functions

def deny(user, record):
    """Deny access."""
    return False


def allow(user, record):
    """Allow access."""
    return True


def get_access_set(access, set):
    try:
        return access[set]
    except KeyError:
        return []


def is_public(data, action):
    """Check if the record is fully public.
    In practice this means that the record doesn't have the ``access`` key or
    the action is not inside access or is empty.
    """
    return '_access' not in data or not data.get('_access', {}).get(action)


def log_action(user, action):
    try:
        email = user.email
    except AttributeError:
        email = 'Anonymous'
    current_app.logger.debug('Action {action} -  user {usr} authenticated: {status}'.format(
        action=action,
        usr=email,
        status=user.is_authenticated
    ))
