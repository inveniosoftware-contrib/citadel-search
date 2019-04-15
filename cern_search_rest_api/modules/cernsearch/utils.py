#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods for CERN Search records."""

from flask import g


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]
