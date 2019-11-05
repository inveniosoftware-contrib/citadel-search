# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Unit tests fixtures."""

import pytest

from invenio_app.factory import create_app
from flask_login import AnonymousUserMixin, UserMixin

@pytest.fixture(scope='module')
def app():
    """Application factory fixture."""
    # FIXME: use pytest-invenio
    # Applies to all calls of `with_app_context`
    return create_app()


@pytest.fixture()
def anonymous_user():
    """Anonymous user (not logged in)."""
    class User(AnonymousUserMixin):

        def __init__(self):
            super().__init__()

    return User()


@pytest.fixture()
def authenticated_user():
    """Authenticated user (logged in)."""
    class User(UserMixin):

        def __init__(self):
            super().__init__()

    return User()


@pytest.fixture(scope='function')
def private_access_record():
    """Private access record."""
    return {
        '_access': {
            'read': ['read-perm'],
            'update': ['update-perm'],
            'delete': ['delete-perm'],
            'owner': ['owner-perm']
        }
    }


@pytest.fixture(scope='function')
def public_access_record():
    """Public access record."""
    return {
        '_access': {
            'update': ['update-perm'],
            'delete': ['delete-perm'],
            'owner': ['owner-perm']
        }
    }
