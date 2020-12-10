#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods for CERN Search records."""

from elasticsearch import VERSION as ES_VERSION
from flask import current_app, g
from flask_login import current_user
from invenio_indexer.utils import default_record_to_index, schema_to_index
from invenio_search import current_search, current_search_client
from invenio_search.utils import prefix_index


def get_user_provides():
    """Extract the user's provides from g."""
    current_app.logger.debug("Identity: %s", g.identity)
    current_app.logger.debug("Current User: %s", current_user)

    return [need.value for need in g.identity.provides]


def record_from_index(record):
    """Get index/doc_type given a record.

    It tries to extract from `record['$schema']` the index and doc_type.
    If it fails, return the default values.

    :param record: The record object.
    :returns: Tuple (index, doc_type).
    """
    index_names = current_search.mappings.keys()
    schema = record.get("metadata").get("$schema", "")
    if isinstance(schema, dict):
        schema = schema.get("$ref", "")

    index, doc_type = schema_to_index(schema, index_names=index_names)

    if index and doc_type:
        return index, doc_type
    else:
        return (
            current_app.config["INDEXER_DEFAULT_INDEX"],
            current_app.config["INDEXER_DEFAULT_DOC_TYPE"],
        )


def default_record_to_mapping(record):
    """Get mapping given a record.

    It tries to extract from `record['$schema']` the index and doc_type.
    If it fails, uses the default values.

    :param record: The record object.
    :returns: mapping
    """
    index, doc = default_record_to_index(record)
    index = prefix_index(index)
    current_app.logger.debug("Using index %s and doc %s", index, doc)

    mapping = current_search_client.indices.get_mapping([index])
    if mapping is not None:
        doc_type = next(iter(mapping))
        current_app.logger.debug("Using mapping for %s", index)
        current_app.logger.debug("Mapping %s", mapping)

        if ES_VERSION[0] >= 7:
            return mapping[doc_type]["mappings"]

        return mapping[doc_type]["mappings"][doc]

    return None


def reverse_dict_list(org):
    """Reverses dict {a: [b,c]} to {b:a, c:a}."""
    newdict = {}
    for key, value in org.items():
        for string in value:
            newdict[string] = key
    return newdict
