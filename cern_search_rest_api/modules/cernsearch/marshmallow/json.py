#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Marshmallow for records and search results."""


from invenio_records_rest.schemas import RecordMetadataSchemaJSONV1
from invenio_records_rest.schemas.json import RecordSchemaJSONV1
from marshmallow import ValidationError, fields, validates_schema


class CSASRecordSchemaV1(RecordMetadataSchemaJSONV1):
    """Record schema."""

    @validates_schema(pass_original=True)
    def validate_record(self, data, original_data, **kwargs):
        """Validate record."""
        if not original_data.get('_access'):
            raise ValidationError('Missing field _access')
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
        if not original_data.get('_data'):
            raise ValidationError('Missing field _data')
        return


class CSASRecordSearchSchemaJSONV1(RecordSchemaJSONV1):
    """Record Search schema."""

    highlight = fields.Raw()
    explanation = fields.Raw()
