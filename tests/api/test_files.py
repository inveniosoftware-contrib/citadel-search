# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Files tests."""
import json
from http import HTTPStatus
from urllib.parse import quote_plus

from flask import current_app
from tests.api.helpers import assert_file, get_headers, get_json, get_schemas_endpoint
from werkzeug.security import gen_salt


def test_file_ops(app, appctx, db, client, user, location):
    """Test file operations."""
    headers = get_headers()

    body = {
        "_access": {
            "read": ["CernSearch-Administrators@cern.ch"],
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "Test default search field",
        },
        "url": "my-domain.com/my-file",
        "$schema": get_schemas_endpoint("test/file_v0.0.4.json")
    }

    # Create test record
    res = client.post('/records/', headers=get_headers(), data=json.dumps(body))
    res_json = get_json(res, code=HTTPStatus.CREATED)

    control_number = res_json['metadata']['control_number']
    bucket = res_json['metadata']['_bucket']
    bucket_content = res_json['metadata']['_bucket_content']

    first_file = 'test.txt'
    second_file = 'test-another.pdf'

    cases = [
        # first upload
        dict(
            name=first_file,
            content=b'test',
        ),
        # update content
        dict(
            name=first_file,
            content=b'test 2',
        ),
        # update file
        dict(
            name=second_file,
            content=b'test 3',
        ),
    ]

    for case in cases:
        # Upload file content
        url = f"/record/{control_number}/files/{case['name']}"
        res = client.put(url, data=case['content'], headers=headers)
        assert res.status_code == HTTPStatus.OK

        # Get record maintains metadata
        res = client.get(f"/record/{control_number}", headers=headers)
        res_json = get_json(res, code=HTTPStatus.OK)
        assert bucket == res_json['metadata']['_bucket']
        assert bucket_content == res_json['metadata']['_bucket_content']
        assert body['url'] == res_json['metadata']['url']

        # Get file content
        res = client.get(url, headers=headers)
        assert_file(res, case['content'], HTTPStatus.OK)

        # Search file content

        # Needed to allow ES to process the file
        import time
        time.sleep(2)

        res = client.get(
            '/records/',
            query_string={'q': quote_plus(case["content"]), 'access': 'CernSearch-Administrators'},
            headers=get_headers()
        )
        assert res.status_code == HTTPStatus.OK

        res_hits = res.json['hits']

        assert res_hits.get('total') == 1
        assert case['name'] == res_hits['hits'][0]['metadata']['file']
        assert case['content'].decode() in res_hits['hits'][0]['metadata']['_data']['content']

    file_url = f"/record/{control_number}/files/{second_file}"

    # Get file - unauthenticated
    res = client.get(file_url)
    assert res.status_code == HTTPStatus.NOT_FOUND

    # Get file - wrong auth
    invalid_token = gen_salt(current_app.config.get('OAUTH2SERVER_TOKEN_PERSONAL_SALT_LEN'))
    res = client.get(file_url, headers=get_headers(invalid_token))
    assert res.status_code == HTTPStatus.NOT_FOUND

    # List files - blocked action
    res = client.get(f'/records/{control_number}/files', headers=headers)
    assert res.status_code == HTTPStatus.NOT_FOUND

    # File does not exists / not processed yet
    assert client.get(f"/record/{control_number}/files/invalid", headers=headers).status_code == HTTPStatus.NOT_FOUND

    # Delete file
    assert client.delete(file_url, headers=headers).status_code == HTTPStatus.NO_CONTENT
    assert client.get(file_url, headers=headers).status_code == HTTPStatus.NOT_FOUND

    # Re Upload file content
    third_file = 'one-more-test.pdf'
    third_file_content = b'test 4'
    file_url = f"/record/{control_number}/files/{third_file}"

    res = client.put(file_url, data=third_file_content, headers=headers)
    assert res.status_code == HTTPStatus.OK

    # Get file content
    res = client.get(file_url, headers=headers)
    assert_file(res, third_file_content, HTTPStatus.OK)

    # Update records mantains file content
    body['url'] = "my-domain-changed.com/cdn/my-file"

    res = client.put(f'/record/{control_number}', headers=get_headers(), data=json.dumps(body))
    res_json = get_json(res, code=HTTPStatus.OK)
    assert bucket == res_json['metadata']['_bucket']
    assert bucket_content == res_json['metadata']['_bucket_content']
    assert body['url'] == res_json['metadata']['url']

    res = client.get(file_url, headers=headers)
    assert_file(res, third_file_content, HTTPStatus.OK)

    # Delete record
    assert client.delete(f"/record/{control_number}", headers=headers).status_code == HTTPStatus.NO_CONTENT
    assert client.get(file_url, headers=headers).status_code == HTTPStatus.GONE
