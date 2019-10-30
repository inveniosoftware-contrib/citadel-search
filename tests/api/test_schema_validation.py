# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import json

import pytest
from tests.api.helpers import get_headers, get_schemas_endpoint


@pytest.mark.unit
def test_control_number_update(appctx, base_client):
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "test_control_number_update",
            "description": "Not updated document"
        },
    }

    # Create test record
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    print(resp.data)
    assert resp.status_code == 201

    orig_record = resp.json['metadata']

    # Update without control_number
    body["_data"]['description'] = 'Update with no control number'
    resp = base_client.put(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers(), 
        data=json.dumps(body)
    )

    put_record = resp.json['metadata']
    assert resp.status_code == 200
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Update with a wrong control_number
    body["_data"]['description'] = 'Update with wrong control number'
    resp = base_client.put(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers(),
        data=json.dumps(body)
    )

    put_record = resp.json['metadata']
    assert resp.status_code == 200
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Delete test record
    resp = base_client.delete(
        '/record/{control_number}'.format(control_number=orig_record['control_number']),
        headers=get_headers())

    assert resp.status_code == 204


@pytest.mark.unit
def test_access_fields_existence(appctx, base_client):
    # POST and PUT should follow the same workflow. Only checking POST.
    # Without _access field
    body = {
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access field"
        }
    }
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing field _access"} in resp.json['errors']

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
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.delete"} in resp.json['errors']

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
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.update"} in resp.json['errors']

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
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.owner"} in resp.json['errors']


@pytest.mark.unit
def test_data_field_existence(appctx, base_client):
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

    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing field _data"} in resp.json['errors']
