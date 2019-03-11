#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_rest.errors import RESTValidationError


class InvalidRecordFormatError(RESTValidationError):
    """Invalid query syntax."""

    code = 400
    description = 'Invalid query syntax.'