#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_indexer.signals import before_record_index

from cern_search_rest_api.modules.cernsearch.indexer import csas_indexer_receiver
from cern_search_rest_api.modules.cernsearch.views import build_blueprint


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
        app.extensions["cern-search"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Set up API endpoints for records.
        for k in dir(app.config):
            if k.startswith('CERN_SEARCH'):
                app.config.setdefault(k, getattr(app.config, k))