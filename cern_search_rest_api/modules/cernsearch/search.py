#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Search utilities."""
import base64
import json
import zlib

from elasticsearch_dsl import Q
from flask import current_app, request
from flask_login import current_user
from invenio_records_rest.query import default_search_factory
from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter
from werkzeug.datastructures import MultiDict

from cern_search_rest_api.modules.cernsearch.facets import saas_facets_factory
from cern_search_rest_api.modules.cernsearch.permissions import has_admin_view_permission
from cern_search_rest_api.modules.cernsearch.utils import get_user_provides


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
    public = ~Q("exists", field="_access.read")
    cern_filter = public

    if provides is not None:
        # Filter for restricted records, that the user has access to
        read_restricted = Q("terms", **{"_access.read": provides})
        write_restricted = Q("terms", **{"_access.update": provides})
        delete_restricted = Q("terms", **{"_access.delete": provides})
        # Filter records where the user is owner
        owner = Q("terms", **{"_access.owner": provides})
        # OR all the filters
        cern_filter = public | read_restricted | write_restricted | delete_restricted | owner

    return Q("bool", filter=cern_filter)


def extract_egroups_from_query():
    """Get egroups from access params (access or access_gz).

    Eg: How to build access_gz:
        if len(access_string) > 1024:
            access_string_gz = base64.b64encode(zlib.compress(access_string.encode(), level=9))
    """
    egroups = request.args.get("access", "")
    if egroups:
        return set(egroups.split(","))

    egroups_gz = request.args.get("access_gz", "")
    if egroups_gz:
        egroups_gz_str = zlib.decompress(base64.b64decode(egroups_gz.encode())).decode()
        if egroups_gz_str:
            return set(egroups_gz_str.split(","))

    return set()


def get_egroups():
    """Get egroups from access param, config or authenticated user."""
    egroups = extract_egroups_from_query()

    # If access rights are sent and is admin_view_account
    if egroups and has_admin_view_permission(current_user):
        try:
            if current_app.config["SEARCH_USE_EGROUPS"]:
                return ["{0}@cern.ch".format(egroup) for egroup in egroups]
            else:
                return list(egroups)
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
        default_multifields_qtype = "best_fields"
        default_operator = "OR"

        operator = request.args.get("default_operator", default_operator)
        multifields_type = request.args.get("qtype", default_multifields_qtype)

        if qstr:
            return Q(
                "query_string",
                query=qstr,
                rewrite="top_terms_1000",  # calculates score for wildcards queries
                type=multifields_type,
                default_operator=operator,
            )
        return Q()

    search, urlkwargs = default_search_factory(self, search, _csas_query_parser)  # type: RecordCERNSearch, MultiDict

    search_index = getattr(search, "_original_index", search._index)[0]
    search, urlkwargs = saas_facets_factory(search, search_index)

    current_app.logger.debug("Search object: %s", str(json.dumps(search.to_dict())))

    search = search.params(search_type="dfs_query_then_fetch")  # search across all shards

    highlights = request.args.getlist("highlight", None)
    if highlights:
        search = search.highlight_options(encoder="html").highlight(*highlights)

    excludes = request.args.getlist("exclude", None)
    if excludes:
        search = search.source(excludes=excludes)

    explain = request.args.get("explain", None)
    if explain:
        search = search.extra(explain=explain)

    search = search.extra(stored_fields=["*"], _source=True)

    return search, urlkwargs


csas_search_factory = search_factory
