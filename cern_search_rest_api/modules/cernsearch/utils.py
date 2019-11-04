#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods for CERN Search records."""

from flask import current_app, g
from invenio_search import current_search
from invenio_search.utils import schema_to_index


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]


def record_from_index(record):
    """Get index/doc_type given a record.

    It tries to extract from `record['$schema']` the index and doc_type.
    If it fails, return the default values.

    :param record: The record object.
    :returns: Tuple (index, doc_type).
    """
    index_names = current_search.mappings.keys()
    schema = record.get('metadata').get('$schema', '')
    if isinstance(schema, dict):
        schema = schema.get('$ref', '')

    index, doc_type = schema_to_index(schema, index_names=index_names)

    if index and doc_type:
        return index, doc_type
    else:
        return (current_app.config['INDEXER_DEFAULT_INDEX'],
                current_app.config['INDEXER_DEFAULT_DOC_TYPE'])
