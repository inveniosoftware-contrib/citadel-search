# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from http import HTTPStatus

import pytest
from flask import current_app, url_for


@pytest.mark.unit
def test_view1(appctx, base_client):
    resp = base_client.post("/account/settings/applications/", follow_redirects=True)
    #resp = base_client.post(url_for("remoteaccount.action_view"), follow_redirects=True)
    print(resp.data)

    assert resp.status_code == HTTPStatus.OK
