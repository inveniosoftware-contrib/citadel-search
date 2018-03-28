#!/usr/bin/python
# -*- coding: utf-8 -*-

"""CERN Search WSGI app instantiation."""

from __future__ import absolute_import, division, print_function

from .factory import create_api

application = create_api()