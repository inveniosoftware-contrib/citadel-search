# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test helpers."""

import os
from urllib.parse import urlunparse

from pytest_invenio.fixtures import appctx


def get_headers():
    api_token = os.environ['API_TOKEN']

    return {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }


def get_schemas_endpoint(appctx, schema):
    host_setting = appctx.config['JSONSCHEMAS_HOST']
    url_scheme = appctx.config['JSONSCHEMAS_URL_SCHEME']
    schemas_path = appctx.config['JSONSCHEMAS_ENDPOINT']
    url_path = "{path}/{schema}".format(path=schemas_path, schema=schema)

    return urlunparse((url_scheme, host_setting, url_path, "", "", ""))
