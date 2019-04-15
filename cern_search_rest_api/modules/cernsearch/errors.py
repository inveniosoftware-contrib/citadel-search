#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from invenio_rest.errors import RESTValidationError


class InvalidRecordFormatError(RESTValidationError):
    """Invalid query syntax."""

    code = 400
    description = 'Invalid query syntax.'