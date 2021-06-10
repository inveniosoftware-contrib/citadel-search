#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Custom errors."""

from invenio_rest.errors import RESTException, RESTValidationError


class InvalidRecordFormatError(RESTValidationError):
    """Invalid query syntax."""

    code = 400
    description = "Invalid query syntax."


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


class Error(object):
    """Represents a generic error.

    .. note:: This is not an actual exception.
    """

    def __init__(self, cause: str):
        """Init object.

        :param cause: The string error.
        """
        self.res = dict(cause=cause)

    def to_dict(self):
        """Convert to dictionary.

        :returns: A dictionary with field, message and, if initialized, the
            HTTP status code.
        """
        return self.res


class ConflictError(RESTException):
    """Conflict Error exception."""

    code = 409
    description = "An internal error occurred due to a conflict in the internal state."
