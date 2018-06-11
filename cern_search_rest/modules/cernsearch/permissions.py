#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_security import current_user
from flask import request, g, current_app
from invenio_indexer.utils import default_record_to_index
from invenio_search import current_search_client

from cern_search_rest.modules.cernsearch.utils import get_user_provides

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
            return cls(record, has_owner_permission, user)
        elif action in cls.read_actions:
            return cls(record, has_read_record_permission, user)
        elif action in cls.update_actions:
            return cls(record, has_update_permission, user)
        elif action in cls.delete_actions:
            return cls(record, has_delete_permission, user)
        else:
            return cls(record, deny, user)


def has_owner_permission(user, record=None):
    """Check if user is authenticated and has create access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        es_index, doc = get_index_from_request(record)
        if current_search_client.indices.exists([es_index]):
            mapping = current_search_client.indices.get_mapping([es_index])
            if mapping is not None:
                # set.isdisjoint() is faster than set.intersection()
                create_access_groups = mapping[es_index]['mappings'][doc]['_meta']['_owner'].split(',')
                if user_provides and not set(user_provides).isdisjoint(set(create_access_groups)):
                    return True
    return False


def get_index_from_request(record=None):
    if record is not None and record.get('$schema', '') is not None:
        return default_record_to_index(record)
    return (current_app.config['INDEXER_DEFAULT_INDEX'],
            current_app.config['INDEXER_DEFAULT_DOC_TYPE'])


def has_update_permission(user, record):
    """Check if user is authenticated and has update access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        update_access_groups = record['_access']['update']
        if check_elasticsearch(record) and user_provides and has_owner_permission(user) and \
            (
                not set(user_provides).isdisjoint(set(update_access_groups))
                or is_admin(user)
            ):
            return True
    return False


def has_read_record_permission(user, record):
    """Check if user is authenticated and has read access. This implies reading one document"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        read_access_groups = record['_access']['read']
        if check_elasticsearch(record) and user_provides and has_owner_permission(user) and \
            (
                not set(user_provides).isdisjoint(set(read_access_groups))
                or is_admin(user)
            ):
            return True
    return False


def has_delete_permission(user, record):
    """Check if user is authenticated and has delete access"""
    if user.is_authenticated:
        # Allow based in the '_access' key
        user_provides = get_user_provides()
        # set.isdisjoint() is faster than set.intersection()
        delete_access_groups = record['_access']['delete']
        if check_elasticsearch(record) and user_provides and has_owner_permission(user) and \
            (
                not set(user_provides).isdisjoint(set(delete_access_groups))
                or is_admin(user)
            ):
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
            return True
    return False


# Utility functions


def deny(user, record):
    """Deny access."""
    return False


def allow(user, record):
    """Allow access."""
    return True


def is_admin(user):
    """Check if the user is administrator"""
    admin_user = current_app.config['ADMIN_USER']
    if user.email == admin_user or user.email.replace('@cern.ch', '') == admin_user:
        return True
    return False


def is_public(data, action):
    """Check if the record is fully public.
    In practice this means that the record doesn't have the ``access`` key or
    the action is not inside access or is empty.
    """
    return '_access' not in data or not data.get('_access', {}).get(action)


def check_elasticsearch(record=None):
    if record is not None:
        """Try to search for given record."""
        search = request._methodview.search_class()
        search = search.get_record(str(record.id))
        return search.count() == 1
    return False
