#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

invenio users create test@example.com --password password --active
invenio roles create search-admin
invenio roles add test@example.com search-admin
invenio tokens create -n test -u test@example.com > .api_token
echo TOKEN: $(<.api_token)
