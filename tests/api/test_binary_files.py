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

BINARY_CONTENT = "e1xydGYxXGFuc2kNCkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0DQpccGFyIH0"


@pytest.mark.unit
@pytest.mark.skip(reason=None)
def test_binary_es_ocr(appctx, base_client):
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "Test binary",
            "description": "Test binary with ingest pipeline",
            "link": "localhost/test",
            "b64": BINARY_CONTENT
        },
        "$schema": get_schemas_endpoint(appctx, "test/binary_v0.0.2.json")
    }

    # Create test record
    resp = base_client.post('/records/', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 201
    print(resp.data)

    # Check non presence of OCR content in DB record
    resp_body = resp.json['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('content') is None  # Content is the target field in ES pipeline
    assert resp_data.get('title') == 'Test binary'
    assert resp_data.get('description') == 'Test binary with ingest pipeline'
    assert resp_data.get('link') == 'localhost/test'
    #TODO: is failling
    assert resp_data.get('b64', None) is None

    control_number = resp_body.get("control_number")
    # Search record
    # Needed to allow ES to process the file
    import time
    time.sleep(2)
    resp = base_client.get(
        '/records/?q=control_number:{control_number}'.format(control_number=control_number),
        headers=get_headers(), 
        data=json.dumps(body)
    )

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 1

    content = resp_hits['hits'][0]['metadata'].get("_data").get('content')
    assert content is not None
    assert content.get('content') == "Lorem ipsum dolor sit amet"
    assert content.get('content_type') == 'application/rtf'

    # Test search over extracted fields
    resp = base_client.get('/records/?q=lorem', headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json['hits']
    assert resp_hits.get('total') == 1

    content = resp_hits['hits'][0]['metadata'].get("_data").get('content')
    assert content is not None
    assert content.get('content') == "Lorem ipsum dolor sit amet"
    assert content.get('content_type') == 'application/rtf'

    # Clean the instance. Delete record
    resp = base_client.delete(
        '/record/{control_number}'.format(control_number=control_number),
        headers=get_headers(), 
        data=json.dumps(body)
    )

    assert resp.status_code == 204
