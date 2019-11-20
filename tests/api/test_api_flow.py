# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""API tests."""

from .helpers import get_headers


def test_testclient(base_client):
    """Test Client."""
    res = base_client.get('/records/', headers=get_headers())

    assert res.json == {
        "aggregations": {},
        "hits": {
            "hits": [],
            "total": 0
        },
        "links": {
            "self": "http://localhost/records/?size=10&page=1"
        }
    }
