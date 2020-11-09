# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from __future__ import absolute_import, print_function

import logging

import pytest
from flask import current_app
from invenio_accounts.models import Role, User
from invenio_oauth2server.models import Token


@pytest.fixture()
def app(app, logger):
    """Application factory fixture."""
    yield app


@pytest.fixture()
def user(db, app):
    """File system location."""
    user = User(email='test@example.com', active=True)
    db.session.add(user)

    role = Role(name='CernSearch-Administrators@cern.ch')
    role.users.append(user)
    db.session.add(role)

    db.session.commit()

    token = Token.create_personal('test', user.id)
    db.session.commit()

    app.config['API_TOKEN'] = token.access_token
    app.config['SEARCH_USE_EGROUPS'] = True

    yield user


@pytest.fixture(scope='module')
def app_config(app_config):
    """Application configuration fixture."""
    # Missing because they're set in invenio base image:
    # More info: https://github.com/inveniosoftware/docker-invenio#environment-variables
    app_config['WORKING_DIR'] = '/opt/invenio'
    app_config['USER_ID'] = 1000
    app_config['INSTANCE_PATH'] = '/opt/invenio/var/instance'

    return app_config


@pytest.fixture()
def logger(appctx, caplog):
    """Set logger level to debug."""
    current_app.logger.setLevel(logging.DEBUG)


@pytest.fixture(scope='module')
def instance_path():
    """Connect instance path.

    Overwrite pytest-invenio fixture to avoid setting static folder to
    `os.path.join(sys.prefix, 'var/instance/static')`
    """
    pass
