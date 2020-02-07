#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Custom errors."""

from invenio_rest.errors import RESTValidationError


class InvalidRecordFormatError(RESTValidationError):
    """Invalid query syntax."""

    code = 400
    description = 'Invalid query syntax.'


class SearchError(Exception):
    """Base class for Search errors."""

    def __init__(self, message):
        """Initialize exception."""
        self.message = message


class ObjectNotFoundError(SearchError):
    """Base class for Search errors."""

    def __str__(self):
        """Return description."""
        return f"{self.message} not found."
