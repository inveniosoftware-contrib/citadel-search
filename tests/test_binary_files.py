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

BINARY_CONTENT = "e1xydGYxXGFuc2kNCkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0DQpccGFyIH0"


@pytest.mark.unit
def test_binary_es_ocr(endpoint, api_key):
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

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
            "b64": "{binary_content}".format(binary_content=BINARY_CONTENT)
        },
        "$schema": "{endpoint}/schemas/test/binary_v0.0.2.json".format(
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
    assert resp_data.get('content') is None  # Content is the target field in ES pipeline
    assert resp_data.get('title') == 'Test binary'
    assert resp_data.get('description') == 'Test binary with ingest pipeline'
    assert resp_data.get('link') == 'localhost/test'
    assert resp_data.get('b64', None) is None

    control_number = resp_body.get("control_number")
    # Search record
    # Needed to allow ES to process the file
    import time
    time.sleep(2)
    resp = requests.get('{endpoint}/api/records/?q=control_number:{control_number}'
                        .format(endpoint=endpoint, control_number=control_number),
                        headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 1

    content = resp_hits['hits'][0]['metadata'].get("_data").get('content')
    assert content is not None
    assert content.get('content') == "Lorem ipsum dolor sit amet"
    assert content.get('content_type') == 'application/rtf'

    # Test search over extracted fields
    resp = requests.get('{endpoint}/api/records/?q=lorem'
                        .format(endpoint=endpoint),
                        headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 1

    content = resp_hits['hits'][0]['metadata'].get("_data").get('content')
    assert content is not None
    assert content.get('content') == "Lorem ipsum dolor sit amet"
    assert content.get('content_type') == 'application/rtf'

    # Clean the instance. Delete record
    resp = requests.delete('{endpoint}/api/record/{control_number}'
                           .format(endpoint=endpoint, control_number=control_number),
                           headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 204
