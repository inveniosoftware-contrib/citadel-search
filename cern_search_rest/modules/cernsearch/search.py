#!/usr/bin/python
# -*- coding: utf-8 -*-
from elasticsearch_dsl import Q
from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter

from cern_search_rest.modules.cernsearch.utils import get_user_provides


def cern_search_filter():
    """Filter list of results."""
    # Get CERN user's provides
    provides = get_user_provides()  # TODO CHANGE THIS BY LIST PROVIDED BY SERVICE

    # Filter for public records
    public = ~Q('exists', field='_access.read')
    # Filter for restricted records, that the user has access to
    read_restricted = Q('terms', **{'_access.read': provides})
    write_restricted = Q('terms', **{'_access.update': provides})
    # Filter records where the user is owner
    owner = Q('terms', **{'_access.owner': provides})
    # OR all the filters
    combined_filter = public | read_restricted | write_restricted | owner

    return Q('bool', filter=[combined_filter])


class RecordCERNSearch(RecordsSearch):
    """CERN search class."""

    class Meta:
        doc_types = None
        default_filter = DefaultFilter(cern_search_filter)
