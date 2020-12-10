#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test helpers."""

import json
from urllib.parse import urlunparse

from flask import current_app


def get_headers(token=None):
    """Build headers."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token or current_app.config['API_TOKEN']}",
    }


def get_schemas_endpoint(schema):
    """Build schemas endpoint."""
    host_setting = current_app.config["JSONSCHEMAS_HOST"]
    url_scheme = current_app.config["JSONSCHEMAS_URL_SCHEME"]
    schemas_path = current_app.config["JSONSCHEMAS_ENDPOINT"]
    url_path = "{path}/{schema}".format(path=schemas_path, schema=schema)

    return urlunparse((url_scheme, host_setting, url_path, "", "", ""))


def get_json(response, code=None):
    """Extract json from response."""
    data = response.get_data(as_text=True)
    if code is not None:
        assert response.status_code == code, data
    return json.loads(data)


def assert_file(response, expected, code):
    """Assert file response."""
    data = response.get_data(as_text=True)
    assert response.status_code == code, data == expected
