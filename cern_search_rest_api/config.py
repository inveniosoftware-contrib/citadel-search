#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Configuration for Citadel Search."""

from __future__ import absolute_import, print_function

import ast
import copy
import os

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.facets import regex_aggregation, simple_query_string
from cern_search_rest_api.modules.cernsearch.indexer import CernSearchRecordIndexer
from cern_search_rest_api.modules.cernsearch.permissions import (record_create_permission_factory,
                                                                 record_delete_permission_factory,
                                                                 record_list_permission_factory,
                                                                 record_read_permission_factory,
                                                                 record_update_permission_factory)
from elasticsearch_dsl import A
from flask import request
from invenio_oauthclient.contrib import cern_openid
from invenio_records_rest import config as irr_config
from invenio_records_rest.facets import terms_filter
from kombu import Exchange, Queue


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Theme
# =====
THEME_SEARCHBAR = False

# OAuth Client
# ============

OAUTHCLIENT_CERN_OPENID_ALLOWED_ROLES = ["search-user", "search-admin"]

CERN_REMOTE_APP = copy.deepcopy(cern_openid.REMOTE_APP)
CERN_REMOTE_APP["params"].update(dict(request_token_params={
    "scope": "openid",
}))

OAUTHCLIENT_REMOTE_APPS = dict(
    cern_openid=CERN_REMOTE_APP,
)

# OAuth REST Client
# ============

OAUTH_REMOTE_REST_APP = copy.deepcopy(cern_openid.REMOTE_REST_APP)
OAUTH_REMOTE_REST_APP["params"].update(dict(request_token_params={
    "scope": "openid",
}))

OAUTHCLIENT_REST_REMOTE_APPS = dict(
    cern_openid=OAUTH_REMOTE_REST_APP,
)

# Accounts
# ========
# FIXME: Needs to be disable for role base auth in SSO. If not invenio_account/sessions:login_listener will crash

ACCOUNTS_SESSION_ACTIVITY_ENABLED = False
SERVER_NAME = os.getenv("CERN_SEARCH_SERVER_NAME")

# Admin
# =====

ADMIN_PERMISSION_FACTORY = 'cern_search_rest_api.modules.cernsearch.permissions:admin_permission_factory'

# JSON Schemas configuration
# ==========================

JSONSCHEMAS_ENDPOINT = '/schemas'
JSONSCHEMAS_HOST = '0.0.0.0'
# Do not register the endpoints on the UI app."""
JSONSCHEMAS_REGISTER_ENDPOINTS_UI = True

# Search configuration
# =====================

SEARCH_MAPPINGS = [os.getenv('CERN_SEARCH_INSTANCE', 'test')]
SEARCH_USE_EGROUPS = ast.literal_eval(os.getenv('CERN_SEARCH_USE_EGROUPS', 'True'))
SEARCH_DOC_PIPELINES = ast.literal_eval(os.getenv('CERN_SEARCH_DOC_PIPELINES', '{}'))

# Alias instance - don't allow updates, allow only search
SEARCH_INSTANCE_IMMUTABLE = ast.literal_eval(os.getenv('CERN_SEARCH_INSTANCE_IMMUTABLE', 'False'))

# Records REST configuration
# ===========================

#: Records REST API configuration

_Record_PID = 'pid(recid, record_class="cern_search_rest_api.modules.cernsearch.api:CernSearchRecord")'  # TODO

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'docid': '/files',
    }
}

FILES_REST_PERMISSION_FACTORY = 'cern_search_rest_api.modules.cernsearch.permissions:files_permission_factory'

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
        record_class=CernSearchRecord,
        indexer_class=CernSearchRecordIndexer,
        record_serializers={
            'application/json': ('cern_search_rest_api.modules.cernsearch.serializers'
                                 ':json_v1_response'),
        },
        record_loaders={
            'application/json': ('cern_search_rest_api.modules.cernsearch.loaders:'
                                 'csas_loader'),
            'application/json-patch+json': lambda: request.get_json(force=True)
        },
        search_class='cern_search_rest_api.modules.cernsearch.search.RecordCERNSearch',
        search_index=os.getenv('CERN_SEARCH_INSTANCE', 'test'),
        search_serializers={
            'application/json': ('cern_search_rest_api.modules.cernsearch.serializers'
                                 ':json_v1_search'),
        },
        search_factory_imp='cern_search_rest_api.modules.cernsearch.search.csas_search_factory',
        max_result_window=10000,
        read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=record_list_permission_factory,
        create_permission_factory_imp=record_create_permission_factory,
        update_permission_factory_imp=record_update_permission_factory,
        delete_permission_factory_imp=record_delete_permission_factory,
        suggesters={
            'phrase': {
                'completion': {
                    'field': 'suggest_keywords',
                }
            },
        },
    )
)


def aggs_filter(field):
    """Create a term filter.

    :param field: Field name.
    :returns: Function that returns the Terms query.
    """
    def inner(values):
        return A('terms', field=field, include=f'.*{values[0]}.*')
    return inner


RECORDS_REST_FACETS = {
    'webservices': {
        'aggs': {
            'collection': {
                'terms': {'field': 'collection'}
            },
            'type_format': {
                'terms': {'field': 'type_format'}
            },
            'author': regex_aggregation('_data.authors.exact_match', 'authors_suggest'),
            'site': regex_aggregation('_data.site.exact_match', 'sites_suggest'),
            'keyword': regex_aggregation('_data.keywords.exact_match', 'keywords_suggest')
        },
        'filters': {
            'collection': terms_filter("collection"),
            'type_format': terms_filter("type_format"),
            'author': terms_filter("_data.authors.exact_match"),
            'site': terms_filter("_data.site.exact_match"),
            'keyword': terms_filter("_data.keywords.exact_match"),
        },
        'matches': {
            'author_match': simple_query_string("_data.authors"),
            'keyword_match': simple_query_string("_data.keywords"),
            'site_match': simple_query_string("_data.site"),
            'name_match': simple_query_string("_data.name"),
            'url_match': simple_query_string("url"),
        }
    },
    'indico': {
        'aggs': {
            'event_type': {
                'terms': {'field': '_data.event_type'}
            },
            'speakers_chairs': {
                'terms': {'field': '_data.speakers_chairs.exact_match'}
            },
            'list_of_persons': {
                'terms': {'field': '_data.list_of_persons.exact_match'}
            }
        }
    }
}

RECORDS_REST_SORT_OPTIONS = {
    'webservices': {
        'bestmatch': {
            'fields': ['-_score'],
            'title': 'Best match',
            'default_order': 'asc',
        },
        'mostrecent': {
            'fields': ['_updated'],
            'title': 'Newest',
            'default_order': 'asc',
        }
    },
    'edms': {
        'bestmatch': {
            'fields': ['-_score'],
            'title': 'Best match',
            'default_order': 'asc',
        },
        'mostrecent': {
            'fields': ['_updated'],
            'title': 'Newest',
            'default_order': 'asc',
        }
    }
}

RECORDS_REST_ELASTICSEARCH_ERROR_HANDLERS = copy.deepcopy(
    irr_config.RECORDS_REST_ELASTICSEARCH_ERROR_HANDLERS)
RECORDS_REST_ELASTICSEARCH_ERROR_HANDLERS['mapper_parsing_exception'] = \
    'cern_search_rest_api.modules.cernsearch.views:elasticsearch_mapper_parsing_exception_handler'

# App
# ===

APP_HEALTH_BLUEPRINT_ENABLED = True

# CORS
# ====

REST_ENABLE_CORS = True
CORS_SEND_WILDCARD = ast.literal_eval(os.getenv('CERN_SEARCH_CORS_SEND_WILDCARD', 'False'))
CORS_SUPPORTS_CREDENTIALS = ast.literal_eval(os.getenv('CERN_SEARCH_CORS_SUPPORTS_CREDENTIALS', 'True'))

# Flask Security
# ==============
# Avoid error upon registration with email sending
# FIXME flask_security/registrable:40 "Too many values to unpack"
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_CONFIRM_REGISTRATION = False
SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = False  # Avoid user registration outside of CERN SSO
SECURITY_RECOVERABLE = False  # Avoid user password recovery
SESSION_COOKIE_SECURE = True

# Celery Configuration
# ====================
FILES_PROCESSOR_QUEUE = os.getenv("CERN_SEARCH_FILES_PROCESSOR_QUEUE", 'files_processor')
FILES_PROCESSOR_QUEUE_DLX = os.getenv("CERN_SEARCH_FILES_PROCESSOR_QUEUE_DLX", 'files_processor_dlx')
FILES_PROCESSOR_EXCHANGE = os.getenv("CERN_SEARCH_FILES_PROCESSOR_EXCHANGE", 'default')
FILES_PROCESSOR_EXCHANGE_DLX = os.getenv("CERN_SEARCH_FILES_PROCESSOR_EXCHANGE_DLX", 'dlx')

#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = os.getenv('INVENIO_CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672')
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = os.getenv('INVENIO_CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')

CELERY_TASK_QUEUES = {
    Queue(
        name=FILES_PROCESSOR_QUEUE,
        exchange=Exchange(FILES_PROCESSOR_EXCHANGE, type='direct'),
        routing_key=FILES_PROCESSOR_QUEUE,
        queue_arguments={
            'x-dead-letter-exchange': FILES_PROCESSOR_EXCHANGE_DLX,
            'x-dead-letter-routing-key': FILES_PROCESSOR_QUEUE_DLX
        }
    ),
    Queue('celery', Exchange('celery'), routing_key='celery')
}

CELERY_TASK_ROUTES = {
    'cern_search_rest_api.modules.cernsearch.tasks.process_file_async': {
        'queue': FILES_PROCESSOR_QUEUE,
        'routing_key': FILES_PROCESSOR_QUEUE,
    }
}

CELERY_TASK_DEFAULT_QUEUE = 'celery'

CELERY_BROKER_POOL_LIMIT = os.getenv("BROKER_POOL_LIMIT", None)

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
    'max_overflow': int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10)),
    'pool_recycle': int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 300)),  # in seconds
}

SEARCH_CLIENT_CONFIG = dict(
    # allow up to 25 connections to each node
    maxsize=int(os.getenv("ELASTICSEARCH_MAX_SIZE", 5)),
)

# FILE
PROCESS_FILE_META = ast.literal_eval(os.getenv("CERN_SEARCH_PROCESS_FILE_META", 'False'))
