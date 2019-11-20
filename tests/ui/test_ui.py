# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Tests for UI."""

from http import HTTPStatus

import pytest


@pytest.mark.unit
@pytest.mark.skip(reason="TODO:https://gitlab.cern.ch/webservices/cern-search/cern-search-rest-api/issues/89")
def test_view(appctx, base_client):
    """Tests view."""
    resp = base_client.post("/account/settings/applications/", follow_redirects=True)

    assert resp.status_code == HTTPStatus.OK
