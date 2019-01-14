#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.


from invenio_records_rest.loaders.marshmallow import \
    marshmallow_loader
from cern_search_rest_api.modules.cernsearch.marshmallow import \
    CSASRecordSchemaV1

csas_loader = marshmallow_loader(CSASRecordSchemaV1)

__all__ = (
    'csas_loader',
)
