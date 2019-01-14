#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_records_rest.schemas import RecordMetadataSchemaJSONV1
from marshmallow import validates_schema, ValidationError


class CSASRecordSchemaV1(RecordMetadataSchemaJSONV1):

    @validates_schema(pass_original=True)
    def add_unknown_fields(self, data, original_data):
        if not original_data.get('_access'):
            raise ValidationError('Missing field _access.')
        delete = original_data.get('_access').get('delete')
        if not delete or not isinstance(delete, list):
            raise ValidationError('Missing or wrong type (not an array) in '
                                  'field _access.delete')
        update = original_data.get('_access').get('update')
        if not update or not isinstance(update, list):
            raise ValidationError('Missing or wrong type (not an array) in '
                                  'field _access.update')
        owner = original_data.get('_access').get('owner')
        if not owner or not isinstance(owner, list):
            raise ValidationError('Missing or wrong type (not an array) in '
                                  'field _access.owner')
        return
