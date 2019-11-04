#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, print_function

from cern_search_rest_api.modules.cernsearch.marshmallow import CSASRecordSchemaV1, CSASRecordSearchSchemaJSONV1
from invenio_records_rest.serializers.json import JSONSerializer
from invenio_records_rest.serializers.response import record_responsify, search_responsify

# Serializers
# ===========
#: JSON serializer definition.

json_v1 = JSONSerializer(CSASRecordSchemaV1, replace_refs=True)
json_v1_records = JSONSerializer(CSASRecordSearchSchemaJSONV1)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1_records, 'application/json')
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1_records, 'application/json')

__all__ = (
    'json_v1',
    'json_v1_response',
    'json_v1_search',
)
