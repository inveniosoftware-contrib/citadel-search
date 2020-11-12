#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom Facets and factories for result filtering and aggregation.

See :data:`invenio_records_rest.config.RECORDS_REST_FACETS` for more
information on how to specify aggregations and filters.
"""

from __future__ import absolute_import, print_function

from elasticsearch_dsl import A, Q
from flask import current_app, request
from six import text_type
from werkzeug.datastructures import MultiDict


def regex_aggregation(field, query_param):
    """Create a regex aggregation.

    :param field: Field name.
    :param query_param: Query param name.
    :returns: Function that returns the A query.
    """

    def inner():
        value = request.values.get(query_param, type=text_type)
        if value:
            return A('terms', field=field, include=f'.*{value}.*')
        else:
            return A('terms', field=field)

    return inner


def match_filter(field):
    """Create a match query.

    :param field: Field name.
    :returns: Function that returns the match query.
    """

    def inner(values):
        return Q("match", **{field: ' '.join(values)})

    return inner


def query_string(field):
    """Create a query_string query.

    :param field: Field name.
    :returns: Function that returns the match query.
    """

    def inner(values):
        return Q(
            'query_string',
            query=f"{field}:({' '.join(values)})",
            rewrite="top_terms_1000",  # calculates score for wildcards queries
        )

    return inner


def simple_query_string(field):
    """Create a query_string query.

    :param field: Field name.
    :returns: Function that returns the match query.
    """

    def inner(values):
        return Q(
            'simple_query_string',
            query=' '.join(values),
            fields=[field]
        )

    return inner


def match_phrase_filter(field):
    """Create a match_phrase or match query. [WIP: missing checking if inside value there's a string]

    :param field: Field name.
    :returns: Function that returns the match query.
    """

    def inner(values):
        current_app.logger.warning(f"match_phrase_filter: {values}")

        matches = []
        phrase_matches = []
        for value in values:
            current_app.logger.warning(f"value: {value}")

            if not value.startswith("\""):
                matches.append(value)

                continue

            if value.endswith("\"") and len(value) > 1:
                phrase_matches.append(value)

        query_match = Q("match", **{field: ' '.join(matches)})
        query_match_phrase = Q("match_phrase", **{field: ' '.join(phrase_matches)})

        current_app.logger.warning(**{field: ' '.join(matches)})

        if matches and phrase_matches:
            return Q('bool', must=[query_match, query_match_phrase])

        if phrase_matches:
            return query_match_phrase

        return query_match

    return inner


def _create_match_dsl(urlkwargs, definitions):
    """Create a match DSL expression."""
    filters = []
    for name, filter_factory in definitions.items():
        values = request.values.getlist(name, type=text_type)
        if values:
            filters.append(filter_factory(values))
            for v in values:
                urlkwargs.add(name, v)

    return (filters, urlkwargs)


def _match_filter(search, urlkwargs, definitions):
    """Ingest match filter in query."""
    matches, urlkwargs = _create_match_dsl(urlkwargs, definitions)

    for match_ in matches:
        search = search.query(match_)

    return (search, urlkwargs)


def saas_facets_factory(search, index):
    """Add custom items to query.

    It's possible to select facets which should be added to query
    by passing their name in `facets` parameter.
    :param search: Basic search object.
    :param index: Index name.
    :returns: A tuple containing the new search object and a dictionary with
        all fields and values used.
    """
    urlkwargs = MultiDict()

    facets = current_app.config['RECORDS_REST_FACETS'].get(index)
    if facets is not None:
        # Match filter
        search, urlkwargs = _match_filter(search, urlkwargs, facets.get("matches", {}))

    return (search, urlkwargs)
