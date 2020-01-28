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

import pytest


@pytest.fixture(scope='module')
def app_config(app_config):
    del app_config['SECRET_KEY']
    del app_config['SECURITY_PASSWORD_SALT']

    return app_config
