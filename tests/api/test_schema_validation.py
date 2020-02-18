# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Schema validation tests."""

import json
from http import HTTPStatus

import pytest
from tests.api.helpers import get_headers


@pytest.mark.unit
def test_control_number_update(app, client, user):
    """Test control number."""
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "test_control_number_update",
            "description": "Not updated document"
        }
    }

    # Create test record
    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.CREATED

    orig_record = resp.json['metadata']

    # Update without control_number
    body["_data"]['description'] = 'Update with no control number'
    resp = client.put(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers(),
        data=json.dumps(body)
    )

    put_record = resp.json['metadata']
    assert resp.status_code == HTTPStatus.OK
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Update with a wrong control_number
    body["_data"]['description'] = 'Update with wrong control number'
    resp = client.put(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers(),
        data=json.dumps(body)
    )

    put_record = resp.json['metadata']
    assert resp.status_code == HTTPStatus.OK
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Delete test record
    resp = client.delete(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers())

    assert resp.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.unit
def test_access_fields_existence(app, client, user):
    """Test _access field."""
    # POST and PUT should follow the same workflow. Only checking POST.
    # Without _access field
    body = {
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access field"
        }
    }
    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert {"field": "_schema", "message": "Missing field _access", 'parents': []} in resp.json['errors']

    # Without _access.delete field
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access.delete field"
        }
    }
    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert {
               "field": "_schema",
               "message": "Missing or wrong type (not an array) in field _access.delete",
               'parents': []
           } in resp.json['errors']

    # Without _access.update field
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access.update field"
        }
    }
    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert {
               "field": "_schema",
               "message": "Missing or wrong type (not an array) in field _access.update",
               'parents': []
           } in resp.json['errors']

    # Without _access.owner field
    body = {
        "_access": {
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access.owner field"
        }
    }
    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.owner",
            'parents': []} in resp.json['errors']


@pytest.mark.unit
def test_data_field_existence(app, client, user):
    """Test _data field."""
    # Create test record without _data field
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "title": "test_access_fields_existence",
        "description": "No _access field"
    }

    resp = client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert {"field": "_schema", "message": "Missing field _data", 'parents': []} in resp.json['errors']
