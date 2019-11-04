#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from cern_search_rest_api.modules.cernsearch.marshmallow import CSASRecordSchemaV1
from invenio_records_rest.loaders.marshmallow import marshmallow_loader

csas_loader = marshmallow_loader(CSASRecordSchemaV1)

__all__ = (
    'csas_loader',
)
