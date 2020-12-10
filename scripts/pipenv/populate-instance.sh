#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

readonly SYS_PREFIX=$(python -c "import sys; print(sys.prefix)")
readonly INVENIO_INSTANCE_PATH="$SYS_PREFIX/var/instance"

invenio db init
invenio db create
invenio files location --default 'default'  ${INVENIO_INSTANCE_PATH}/data
invenio index init
invenio index list
