# -*- coding: utf-8 -*-
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
        app.extensions["cern-search"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Set up API endpoints for records.
        for k in dir(app.config):
            if k.startswith('CERN_SEARCH'):
                app.config.setdefault(k, getattr(app.config, k))