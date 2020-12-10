#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

invenio db init
invenio db create
invenio files location default ${DEFAULT_RECORDS_FILES_LOCATION} --default
invenio index init
invenio index list
