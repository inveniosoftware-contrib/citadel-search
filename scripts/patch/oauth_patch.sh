#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

readonly LOCATION=$(pip show invenio-oauthclient | grep Location | awk '{print $2}')
readonly SCRIPT_PATH=$(dirname $0)

rm -f ${LOCATION}/invenio_oauthclient/contrib/cern.py
cp ${SCRIPT_PATH}/cern.py ${LOCATION}/invenio_oauthclient/contrib/cern.py
