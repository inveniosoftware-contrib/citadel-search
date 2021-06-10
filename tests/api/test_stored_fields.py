#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Search tests."""

import json
from http import HTTPStatus

import pytest

from tests.api.helpers import get_headers, get_schemas_endpoint


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application configuration fixture."""
    app_config["SEARCH_COPY_TO_METADATA"] = False

    return app_config


def test_testclient(app, appctx, client, user):
    """Test search over public documents.

    Test stored fields default behaviour
    """
    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"],
        },
        "_data": {
            "title": "Test default search field",
            "description": "This contains CernSearch and should appear",
        },
        "$schema": get_schemas_endpoint("test/doc_v0.0.2.json"),
    }

    # Create first test record
    resp = client.post("/records/", headers=get_headers(), data=json.dumps(body))

    assert resp.status_code == HTTPStatus.CREATED

    resp_body = resp.json["metadata"]
    assert resp_body.get("control_number") is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get("title") == "Test default search field"
    assert resp_data.get("description") == "This contains CernSearch and should appear"

    # Needed to allow ES to process the file
    import time

    time.sleep(2)

    resp = client.get("/records/?q=CernSearch", headers=get_headers())
    assert resp.status_code == HTTPStatus.OK

    resp_hits = resp.json["hits"]

    assert resp_hits.get("total") == 1
    title = resp_hits["hits"][0]["metadata"].get("_data").get("title")

    assert title is not None
    assert title == "Test default search field"

    # copy to
    assert resp_hits["hits"][0]["metadata"].get("_data").get("name") is None
    name = resp_hits["hits"][0]["metadata"].get("_data.name")
    assert name is not None
    assert name == ["Test default search field"]

    store = resp_hits["hits"][0].get("stored")
    assert store

    name = resp_hits["hits"][0].get("stored").get("_data.name")
    assert name is not None
    assert name == ["Test default search field"]
