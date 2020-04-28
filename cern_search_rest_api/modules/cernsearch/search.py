#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Search utilities."""

from cern_search_rest_api.modules.cernsearch.utils import get_user_provides
from elasticsearch_dsl import Q
from flask import current_app, request
from invenio_records_rest.query import default_search_factory
from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter
from werkzeug.datastructures import MultiDict


"""
The Filter emulates the following query:
curl -X GET "localhost:9200/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "filter": {
        "bool": {
          "should": [
            {"terms": {"_access.read": ["egroup-read-one","egroup-read-two"]}},
            {"terms": {"_access.update": "egroup-write-one"}},
            {"bool": { # Public document
              "must_not": {
                "exists": {"field": "_access.read"}
              } # End must_not
            }} # End bool
          ] # End should
        } # End bool
      } # End filter
    } # End bool
  } # End query
}
'
"""


def cern_search_filter():
    """Filter list of results."""
    provides = get_egroups()
    # Filter for public records
    public = ~Q('exists', field='_access.read')
    cern_filter = public

    if provides is not None:
        # Filter for restricted records, that the user has access to
        read_restricted = Q('terms', **{'_access.read': provides})
        write_restricted = Q('terms', **{'_access.update': provides})
        delete_restricted = Q('terms', **{'_access.delete': provides})
        # Filter records where the user is owner
        owner = Q('terms', **{'_access.owner': provides})
        # OR all the filters
        cern_filter = public | read_restricted | write_restricted | delete_restricted | owner

    return Q('bool', filter=cern_filter)


def get_egroups():
    """Get egroups from access param, config or authenticated user."""
    egroups = request.args.get('access', None)
    # If access rights are sent or is a search query
    if egroups or (request.path == '/records/' and request.method == 'GET'):
        try:
            if current_app.config['SEARCH_USE_EGROUPS']:
                return ['{0}@cern.ch'.format(egroup) for egroup in egroups.split(',')]
            else:
                return egroups.split(',')
        except AttributeError:
            return None
    # Else use user's token ACLs
    return get_user_provides()


class RecordCERNSearch(RecordsSearch):
    """CERN search class with Elasticsearch DSL."""

    class Meta:
        """Configuration for ``Search`` and ``FacetedSearch`` classes."""

        doc_types = None
        default_filter = DefaultFilter(cern_search_filter)


def search_factory(self, search: RecordCERNSearch, query_parser=None):
    """Parse query using elasticsearch DSL query.

    :param self: REST view.
    :param search: Elastic search DSL search instance.
    :returns: Tuple with search instance and URL arguments.
    """

    def _csas_query_parser(qstr=None):
        """Parse with Q() from elasticsearch_dsl."""
        default_multifields_type = "best_fields"
        multifields_type = request.args.get('type', default_multifields_type)

        if qstr:
            return Q(
                'query_string',
                query=qstr,
                rewrite="scoring_boolean",  # calculates score for wildcards queries
                type=multifields_type
            )
        return Q()

    search, urlkwargs = default_search_factory(self, search, _csas_query_parser)  # type: RecordCERNSearch, MultiDict

    search = search.params(search_type="dfs_query_then_fetch")  # search across all shards

    highlights = request.args.getlist('highlight', None)
    if highlights:
        search = search.highlight(*highlights)

    explain = request.args.get('explain', None)
    if explain:
        search = search.extra(explain=explain)

    return search, urlkwargs


csas_search_factory = search_factory
