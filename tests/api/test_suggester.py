# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import json
import time

import pytest
from tests.api.helpers import get_headers, get_schemas_endpoint


def create_record(appctx, base_client, title):
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": title
        },
        "$schema": get_schemas_endpoint(appctx, "test/suggest_v0.0.2.json")
    }

    # Create test record
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == title

    return resp_body.get("control_number")


@pytest.mark.unit
def test_suggester(appctx, base_client):
    """
    Test search over public documents. Test that the ``_access.*`` field is
    not searched over.
    """

    # Create records
    control_numbers = [
        create_record(appctx, base_client, 'The First Suggestion'),
        create_record(appctx, base_client, 'Documentation site title'),
        create_record(appctx, base_client, 'CERN Search Documentation'),
        create_record(appctx, base_client, 'Invenio docs site'),
        create_record(appctx, base_client, 'The final suggester')
    ]

    time.sleep(3)

    query = {
        "q": 'suggest:the f'
    }

    # 'the f' should return 1st and 5th record
    resp = base_client.get('/records/', query_string=query, headers=get_headers())

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 2

    # 'doc' should return 2nd, 3rd and 4th record
    query['q'] = 'suggest:doc'
    resp = base_client.get('/records/', query_string=query, headers=get_headers())

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 3

    # 'f sugg' should return 1st and 5th record
    query['q'] = 'suggest:f sugg'
    resp = base_client.get('/records/', query_string=query, headers=get_headers())

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 2

    # delete records

    for control_number in control_numbers:
        resp = base_client.delete('/record/{control_number}'.format(control_number=control_number), headers=get_headers())

        assert resp.status_code == 204
