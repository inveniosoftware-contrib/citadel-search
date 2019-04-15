# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import pytest
import requests


@pytest.mark.unit
def test_ui(endpoint, api_key):

    # Check the UI does not generate 50X Errors
    resp = requests.post('{endpoint}/account/settings/applications/'.format(
        endpoint=endpoint))

    assert resp.status_code == 200
