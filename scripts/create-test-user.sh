#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

invenio users create test@example.com --password test1234 --active
export API_TOKEN=$(invenio tokens create -n test -u test@example.com)
echo "API TOKEN: $API_TOKEN"
