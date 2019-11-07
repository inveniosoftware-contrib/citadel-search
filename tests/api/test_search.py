# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import json

from pytest_invenio.fixtures import appctx, base_client
from tests.api.helpers import get_headers, get_schemas_endpoint


def test_testclient(appctx, base_client):
    """
    Test search over public documents. Test that the ``_access.*`` field is
    not searched over.
    """

    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "Test default search field",
            "description": "This contains CernSearch and should appear"
        },
        "$schema": get_schemas_endpoint(appctx, "test/doc_v0.0.2.json")
    }

    # Create first test record
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == 'Test default search field'
    assert resp_data.get('description') == 'This contains CernSearch and should appear'

    control_number_one = resp_body.get("control_number")

    # Create second test record
    body["_data"]['description'] = 'This does not contains the magic word and should not appear'

    # Create test record
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == 'Test default search field'
    assert resp_data.get('description') == 'This does not contains the magic word and should not appear'

    control_number_two = resp_body.get("control_number")

    # # Needed to allow ES to process the file
    import time
    time.sleep(3)

    # Search records
    # Test search with no query
    resp = base_client.get('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 2

    resp = base_client.get('/records/?q=CernSearch', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 1

    description = resp_hits['hits'][0]['metadata'].get("_data").get('description')
    assert description is not None
    assert description == 'This contains CernSearch and should appear'

    # Clean the instance. Delete record
    resp = base_client.delete(
        '/record/{control_number}'.format(control_number=control_number_one),
        headers=get_headers(),
        data=json.dumps(body)
    )

    assert resp.status_code == 204

    resp = base_client.delete(
        '/record/{control_number}'
        .format(control_number=control_number_two),
        headers=get_headers(),
        data=json.dumps(body)
    )

    assert resp.status_code == 204
