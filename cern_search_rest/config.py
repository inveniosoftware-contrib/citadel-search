# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# JSON Schemas configuration
# ==========================

JSONSCHEMAS_ENDPOINT = '/schemas'
JSONSCHEMAS_HOST = '0.0.0.0'
# Do not register the endpoints on the UI app."""
JSONSCHEMAS_REGISTER_ENDPOINTS_UI = False

# Search configuration
# =====================

SEARCH_MAPPINGS = ['records']
# SEARCH_ELASTIC_HOSTS = None # default localhost

# Records REST configuration
# =====================

#: Records REST API configuration

_Record_PID = 'pid(recid, record_class="cern_search_rest.modules.records.api:CernSearchRecord")'  # TODO

RECORDS_REST_ENDPOINTS = dict(
    docid=dict(
        pid_type='recid',
        pid_fetcher='recid',
        pid_minter='recid',
        default_endpoint_prefix=True,
        default_media_type='application/json',
        item_route='/record/<{0}:pid_value>'.format(_Record_PID),
        list_route='/records/',
        links_factory_imp='invenio_records_rest.links:default_links_factory',
        record_class='cern_search_rest.modules.records.api:CernSearchRecord',  # TODO
        # record_loaders={ # TODO
        #    'application/json': 'mypackage.loaders:json_loader'
        # },
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_class=' invenio_search.api.RecordsSearch',
        # search_factory_imp=search_factory(), # Default TODO
        search_index='records',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
        },
        # suggesters= {}, # TODO
        # use_options_view=True, # TODO
        max_result_window=10000,
        read_permission_factory_imp=permission_check_factory(),
        create_permission_factory_imp=deposit_read_permission_factory,
        update_permission_factory_imp=permission_check_factory(),
        delete_permission_factory_imp=deposit_read_permission_factory,
        # error_handlers={}, # TODO
    )
)
