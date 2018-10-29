#!/usr/bin/python
# -*- coding: utf-8 -*-
from elasticsearch_dsl import Q
from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter
from flask import request, current_app

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
            {"nested": {
              "path": "_access", 
              "query": {
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
              } # End query
            }} # End nested
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
    nested_query = public

    if provides is not None:
        # Filter for restricted records, that the user has access to
        read_restricted = Q('terms', **{'_access.read': provides})
        write_restricted = Q('terms', **{'_access.update': provides})
        # Filter records where the user is owner
        owner = Q('terms', **{'_access.owner': provides})
        # OR all the filters
        nested_query = public | read_restricted | write_restricted | owner

    return Q('bool', should=[Q('nested', path='_access', query=nested_query)])


def get_egroups():
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
    """CERN search class."""

    class Meta:
        doc_types = None
        default_filter = DefaultFilter(cern_search_filter)
