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
import time

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": ''
}


def create_record(endpoint, api_key, title):
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": title
        },
        "$schema": "{endpoint}/schemas/test/suggest_v0.0.2.json".format(
            endpoint=endpoint
        )
    }

    # Create test record
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json()['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == title

    return resp_body.get("control_number")


# @pytest.mark.unit
def test_suggester(endpoint, api_key):
    """
    Test search over public documents. Test that the ``_access.*`` field is
    not searched over.
    """
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

    # Create records
    control_numbers = [
        create_record(endpoint, api_key, 'The First Suggestion'),
        create_record(endpoint, api_key, 'Documentation site title'),
        create_record(endpoint, api_key, 'CERN Search Documentation'),
        create_record(endpoint, api_key, 'Invenio docs site'),
        create_record(endpoint, api_key, 'The final suggester')
    ]

    time.sleep(3)

    query = {
        "q": 'suggest:the f'
    }

    # 'the f' should return 1st and 5th record
    resp = requests.get('{endpoint}/api/records/'.format(endpoint=endpoint),
                        params=query,
                        headers=HEADERS)

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 2

    # 'doc' should return 2nd, 3rd and 4th record
    query['q'] = 'suggest:doc'
    resp = requests.get('{endpoint}/api/records/'.format(endpoint=endpoint),
                        params=query,
                        headers=HEADERS)

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 3

    # 'f sugg' should return 1st and 5th record
    query['q'] = 'suggest:f sugg'
    resp = requests.get('{endpoint}/api/records/'.format(endpoint=endpoint),
                        params=query,
                        headers=HEADERS)

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 2

    # delete records

    for control_number in control_numbers:
        resp = requests.delete('{endpoint}/api/record/{control_number}'
                               .format(endpoint=endpoint, control_number=control_number),
                               headers=HEADERS)

        assert resp.status_code == 204
