#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Helper methods for CERN Search records."""

from flask import g
from flask import current_app
from invenio_search import current_search
from invenio_search.utils import schema_to_index, build_index_name


def get_user_provides():
    """Extract the user's provides from g."""
    return [need.value for need in g.identity.provides]


def get_index_from_request(record=None):
    if record is not None and record.get('$schema', '') is not None:
        return cern_search_record_to_index(record)
    current_app.logger.debug('get_index_from_schema(): Record {record} - $schema {schema}. Using defaults'.format(
        record=record,
        schema='No record' if record is None else record.get('$schema')
    ))
    return (current_app.config['INDEXER_DEFAULT_INDEX'],
            current_app.config['INDEXER_DEFAULT_DOC_TYPE'])


def cern_search_record_to_index(record):
    """Get index/doc_type given a record.
    It tries to extract from `record['$schema']` the index and doc_type,
    the index has `CERN_SEARCH_INDEX_PREFIX` as prefix or `CERN_SEARCH_DEFAULT_INDEX_PREFIX`
    if it is not set up to be able to use the ES central service.
    If it fails, return the default values. In this case the prefix is the default value.
    :param record: The record object.
    :returns: Tuple (index, doc_type).
    """

    prefix = current_app.config['INDEX_PREFIX']
    index_names = current_search.mappings.keys()

    schema = record.get('$schema', '')
    if isinstance(schema, dict):
        schema = schema.get('$ref', '')

    parts = schema.split('/')

    if index_names:
        for start in range(len(parts)):
            index_name = build_index_name(*parts[start:])
            if index_name in index_names:
                if index_name.startswith(prefix) and len(index_name) > len(prefix) + 2:
                    return index_name, index_name[len(prefix) + 1:]

    current_app.logger.debug('Index {0} - Doc {1}'.format(
        current_app.config['INDEXER_DEFAULT_INDEX'],
        current_app.config['INDEXER_DEFAULT_DOC_TYPE'])
    )
    return (current_app.config['INDEXER_DEFAULT_INDEX'],
            current_app.config['INDEXER_DEFAULT_DOC_TYPE'])