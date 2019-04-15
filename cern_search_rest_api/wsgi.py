#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CERN Search WSGI app instantiation."""


from __future__ import absolute_import, print_function

from invenio_app.wsgi import application

__all__ = ('application', )