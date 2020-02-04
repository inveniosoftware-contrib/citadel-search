# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Unit tests fixtures."""
from io import BytesIO

import pytest
from flask_login import AnonymousUserMixin, UserMixin
from invenio_app.factory import create_api
from invenio_files_rest.models import Bucket, ObjectVersion


@pytest.fixture(scope='module')
def database(database):
    """Clear database.

    Scope: module

    Remove this after all tests are migrated to fixtures instead of scripts for initialization.
    """
    from invenio_db import db as db_
    from sqlalchemy_utils.functions import database_exists
    if database_exists(str(db_.engine.url)):
        db_.drop_all()
        db_.create_all()

    yield database


@pytest.fixture(scope='function')
def db(database, db):
    """Clear database.

    Scope: function

    Remove this after all tests are migrated to fixtures instead of scripts for initialization.
    """
    yield db


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def anonymous_user():
    """Anonymous user (not logged in)."""
    class User(AnonymousUserMixin):

        def __init__(self):
            super().__init__()

    return User()


@pytest.fixture()
def authenticated_user():
    """Authenticate user (logged in)."""
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


@pytest.fixture()
def bucket(db, location):
    """File system location."""
    b1 = Bucket.create()
    b1.id = '00000000-0000-0000-0000-000000000000'
    db.session.commit()

    yield b1

    b1.remove()
    db.session.commit()


@pytest.fixture()
def objects(db, bucket):
    """Multipart object."""
    content = b'some content'
    obj = ObjectVersion.create(
        bucket,
        'test.pdf',
        stream=BytesIO(content),
        size=len(content)
    )
    db.session.commit()

    yield obj

    ObjectVersion.delete(bucket, obj.key)
    db.session.commit()
