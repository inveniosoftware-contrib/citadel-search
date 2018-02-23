#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Helper methods for CERN Search records."""

from flask import g


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]