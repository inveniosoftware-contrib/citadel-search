# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import json

import pytest
import requests

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": ''
}


@pytest.mark.unit
def test_control_number_update(endpoint, api_key):

    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

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
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 201

    orig_record = resp.json()['metadata']

    # Update without control_number
    body["_data"]['description'] = 'Update with no control number'
    resp = requests.put('{endpoint}/api/record/{control_number}'.format(
                        endpoint=endpoint,
                        control_number=orig_record['control_number']),
                        headers=HEADERS, data=json.dumps(body))

    put_record = resp.json()['metadata']
    assert resp.status_code == 200
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Update with a wrong control_number
    body["_data"]['description'] = 'Update with wrong control number'
    resp = requests.put('{endpoint}/api/record/{control_number}'.format(
        endpoint=endpoint,
        control_number=orig_record['control_number']),
        headers=HEADERS, data=json.dumps(body))

    put_record = resp.json()['metadata']
    assert resp.status_code == 200
    assert put_record.get('control_number') is not None
    assert put_record.get('control_number') == orig_record['control_number']
    assert put_record["_data"]['description'] == body["_data"]['description']

    # Delete test record
    resp = requests.delete('{endpoint}/api/record/{control_number}'.format(
        endpoint=endpoint,
        control_number=orig_record['control_number']),
        headers=HEADERS)

    assert resp.status_code == 204


@pytest.mark.unit
def test_access_fields_existence(endpoint, api_key):
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

    # POST and PUT should follow the same workflow. Only checking POST.
    # Without _access field
    body = {
        "_data": {
            "title": "test_access_fields_existence",
            "description": "No _access field"
        }
    }
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing field _access"} in resp.json()['errors']

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
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.delete"} in resp.json()['errors']

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
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.update"} in resp.json()['errors']

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
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing or wrong type (not an array) in field _access.owner"} in resp.json()['errors']


@pytest.mark.unit
def test_data_field_existence(endpoint, api_key):
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

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

    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 400
    assert {"field": "_schema", "message": "Missing field _data"} in resp.json()['errors']
