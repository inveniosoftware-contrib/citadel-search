#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from cern_search_rest_api.modules.cernsearch.utils import record_from_index
from flask import current_app
from invenio_indexer.utils import default_record_to_index
from invenio_records_rest.schemas import RecordMetadataSchemaJSONV1
from invenio_records_rest.schemas.json import RecordSchemaJSONV1
from marshmallow import ValidationError, post_dump, validates_schema


def has_and_needs_binary(original_data):
    es_index, doc = default_record_to_index(original_data)
    binary_index_list = current_app.config['SEARCH_DOC_PIPELINES']
    if doc in binary_index_list and not original_data.get("_data").get('b64'):
        return False
    return True


class CSASRecordSchemaV1(RecordMetadataSchemaJSONV1):

    @validates_schema(pass_original=True)
    def validate_record(self, data, original_data):
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
        if not has_and_needs_binary(original_data):
            raise ValidationError('Record to be index belongs to binary index '
                                  'but does not contain the [b64] field')
        return


class CSASRecordSearchSchemaJSONV1(RecordSchemaJSONV1):

    @post_dump()
    def remove_base64(self, data):
        """ If needed remove the base64 data from the response """
        es_index, doc = record_from_index(data)
        binary_index_list = current_app.config['SEARCH_DOC_PIPELINES']
        if doc in binary_index_list:
            data.get('metadata').get("_data").pop('b64')
        return data
