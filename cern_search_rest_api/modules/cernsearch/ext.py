#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Cern Search module."""

from cern_search_rest_api.modules.cernsearch.celery import DeclareDeadletter
from cern_search_rest_api.modules.cernsearch.indexer import csas_indexer_receiver
from cern_search_rest_api.modules.cernsearch.receivers import process_file
from cern_search_rest_api.modules.cernsearch.views import build_blueprint
from invenio_celery import InvenioCelery
from invenio_files_rest.signals import file_uploaded
from invenio_indexer.signals import before_record_index


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
        before_record_index.connect(csas_indexer_receiver, sender=app)
        file_uploaded.connect(process_file)

        celery = InvenioCelery(app)
        celery.celery.steps['worker'].add(DeclareDeadletter)

        app.extensions["cern-search"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Set up API endpoints for records.
        for k in dir(app.config):
            if k.startswith('CERN_SEARCH'):
                app.config.setdefault(k, getattr(app.config, k))
