#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helper methods for CERN Search records."""

from flask import g


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]
