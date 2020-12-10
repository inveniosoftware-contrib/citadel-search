#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Cern Search module."""
from celery import current_app as current_celery

from cern_search_rest_api.modules.cernsearch.celery import DeclareDeadletter
from cern_search_rest_api.modules.cernsearch.views import build_blueprint, build_blueprint_record_files_content


class CERNSearch(object):
    """CERN Search extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        blueprint = build_blueprint(app)
        app.register_blueprint(blueprint)

        blueprint_record_files_content = build_blueprint_record_files_content(app)
        app.register_blueprint(blueprint_record_files_content)

        current_celery.steps["worker"].add(DeclareDeadletter)

        self.register_signals(app)

        app.extensions["cern-search"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Set up API endpoints for records.
        for k in dir(app.config):
            if k.startswith("CERN_SEARCH"):
                app.config.setdefault(k, getattr(app.config, k))

    def register_signals(self, app):
        """Register signals."""
        if app.config["SEARCH_FILE_INDEXER"]:
            from cern_search_rest_api.modules.cernsearch.indexer import (
                index_file_content,
            )
            from cern_search_rest_api.modules.cernsearch.receivers import (
                file_deleted_listener,
                file_processed_listener,
                file_uploaded_listener,
                record_deleted_listener,
            )
            from invenio_files_processor.signals import file_processed
            from invenio_files_rest.signals import file_deleted, file_uploaded
            from invenio_indexer.signals import before_record_index
            from invenio_records.signals import after_record_delete

            file_uploaded.connect(file_uploaded_listener)
            file_processed.connect(file_processed_listener)
            file_deleted.connect(file_deleted_listener)
            after_record_delete.connect(record_deleted_listener)
            before_record_index.connect(index_file_content)
