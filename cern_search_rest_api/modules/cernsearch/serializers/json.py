#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow based JSON serializer for records."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers import JSONSerializer

from cern_search_rest_api.modules.cernsearch.serializers.base import CernPreprocessorMixin


class CernJSONSerializer(JSONSerializer, CernPreprocessorMixin):
    """Marshmallow based JSON serializer for records."""
