#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import ast
import copy
import os
from invenio_oauthclient.contrib import cern

from .modules.cernsearch.permissions import (record_read_permission_factory,
                                             record_create_permission_factory,
                                             record_update_permission_factory,
                                             record_delete_permission_factory,
                                             record_list_permission_factory)


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Theme
# =====
THEME_SEARCHBAR = False

# OAuth Client
# ============

CERN_REMOTE_APP = copy.deepcopy(cern.REMOTE_APP)
CERN_REMOTE_APP["params"].update(dict(request_token_params={
    "resource": os.getenv('CERN_SEARCH_REMOTE_APP_RESOURCE', 'test-cern-search.cern.ch'),
    "scope": "Name Email Bio Groups",
}))

CERN_REMOTE_APP["authorized_handler"] = 'cern_search_rest_api.modules.cernsearch.handlers:cern_authorized_signup_handler'

OAUTHCLIENT_REMOTE_APPS = dict(
    cern=CERN_REMOTE_APP,
)

# Accounts
# ========
# FIXME: Needs to be disable for role base auth in SSO. If not invenio_account/sessions:login_listener will crash

ACCOUNTS_SESSION_ACTIVITY_ENABLED = False

# Admin
# =====

ADMIN_PERMISSION_FACTORY = 'cern_search_rest_api.modules.cernsearch.permissions:admin_permission_factory'

# JSON Schemas configuration
# ==========================

JSONSCHEMAS_ENDPOINT = '/schemas'
JSONSCHEMAS_HOST = '0.0.0.0'
# Do not register the endpoints on the UI app."""
JSONSCHEMAS_REGISTER_ENDPOINTS_UI = True

# Indexer
# =======

# TODO use ES central service. Change INDEXER_RECORD_TO_INDEX = 'invenio_indexer.utils.default_record_to_index'

INDEX_PREFIX = os.getenv('CERN_SEARCH_INDEX_PREFIX', 'cernsearch')
INDEXER_DEFAULT_DOC_TYPE = os.getenv('CERN_SEARCH_DEFAULT_DOC_TYPE', 'doc_v0.0.1')
INDEXER_DEFAULT_INDEX = os.getenv('CERN_SEARCH_DEFAULT_INDEX', 'cernsearch-test-doc_v0.0.1')

# Search configuration
# =====================

SEARCH_MAPPINGS = [os.getenv('CERN_SEARCH_INSTANCE', 'cernsearch-test')]
SEARCH_USE_EGROUPS = ast.literal_eval(os.getenv('CERN_SEARCH_USE_EGROUPS', 'True'))

# Records REST configuration
# ===========================

#: Records REST API configuration

_Record_PID = 'pid(recid, record_class="cern_search_rest_api.modules.cernsearch.api:CernSearchRecord")'  # TODO

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
        record_class='cern_search_rest_api.modules.cernsearch.api:CernSearchRecord',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_class='cern_search_rest_api.modules.cernsearch.search.RecordCERNSearch',
        search_index=os.getenv('CERN_SEARCH_INSTANCE', 'cernsearch-test'),
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
        },
        max_result_window=10000,
        read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=record_list_permission_factory,
        create_permission_factory_imp=record_create_permission_factory,
        update_permission_factory_imp=record_update_permission_factory,
        delete_permission_factory_imp=record_delete_permission_factory,
    )
)

# App
# ===

RATELIMIT_DEFAULT = os.getenv('CERN_SEARCH_INSTANCE_RATELIMIT', '5000/hour')
APP_HEALTH_BLUEPRINT_ENABLED = True
APP_HEALTH_BLUEPRINT = 'cern_search_rest_api.modules.cernsearch.views:build_health_blueprint'

# Flask Security
# ==============
# Avoid error upon registration with email sending
# FIXME flask_security/registrable:40 "Too many values to unpack"
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_CONFIRM_REGISTRATION = False
SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = False  # Avoid user registration outside of CERN SSO
SECURITY_RECOVERABLE = False  # Avoid user password recovery
