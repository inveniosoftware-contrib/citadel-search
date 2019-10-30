#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

invenio users create test@example.com --password test1234 --active
invenio roles create CernSearch-Administrators@cern.ch
invenio roles add test@example.com CernSearch-Administrators@cern.ch
invenio tokens create -n test -u test@example.com > .api_token
echo TOKEN: $(<.api_token)
