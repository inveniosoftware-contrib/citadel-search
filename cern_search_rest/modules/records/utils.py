#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Helper methods for CERN Search records."""

from flask import g
from flask import current_app
from invenio_search import current_search
from invenio_search.utils import schema_to_index

INDEX_PREFIX = current_app.config['CERN_SEARCH_DEFAULT_INDEX_PREFIX']


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]


def default_record_to_index(record):
    """Get index/doc_type given a record.
    It tries to extract from `record['$schema']` the index and doc_type,
    the index has `CERN_SEARCH_INDEX_PREFIX` as prefix or `CERN_SEARCH_DEFAULT_INDEX_PREFIX`
    if it is not set up to be able to use the ES central service.
    If it fails, return the default values. In this case the prefix is the default value.
    :param record: The record object.
    :returns: Tuple (index, doc_type).
    """
    index_names = current_search.mappings.keys()
    schema = record.get('$schema', '')
    if isinstance(schema, dict):
        schema = schema.get('$ref', '')
    aux = current_app.config['CERN_SEARCH_INDEX_PREFIX']
    if aux:
        INDEX_PREFIX = aux

    index, doc_type = schema_to_index(schema, index_names=index_names)

    if index and doc_type:
        return '{0}{1}'.format(INDEX_PREFIX,index), doc_type
    else:
        return ('{0}{1}'.format(current_app.config['CERN_SEARCH_DEFAULT_INDEX_PREFIX'],
                                current_app.config['INDEXER_DEFAULT_INDEX']),
                current_app.config['INDEXER_DEFAULT_DOC_TYPE'])
