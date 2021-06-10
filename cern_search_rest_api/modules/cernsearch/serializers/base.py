#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Mixin helper class for preprocessing records and search results."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_records_rest.serializers.base import PreprocessorMixin


class CernPreprocessorMixin(PreprocessorMixin):
    """Base class for serializers."""

    @staticmethod
    def preprocess_search_hit(pid, record_hit, links_factory=None, **kwargs):
        """Prepare a record hit from Elasticsearch for serialization."""
        record = super(CernPreprocessorMixin, CernPreprocessorMixin).preprocess_search_hit(
            pid, record_hit, links_factory=None, **kwargs
        )

        if record_hit.get("fields"):
            # Move attrs from fields to metadata.
            current_app.logger.debug("SEARCH_COPY_TO_METADATA %s", current_app.config["SEARCH_COPY_TO_METADATA"])

            if current_app.config["SEARCH_COPY_TO_METADATA"]:
                for key, value in record_hit["fields"].items():
                    key_path = key.split(".")
                    curr_path = record["metadata"]
                    for path in key_path[:-1]:
                        curr_path[path] = curr_path[path] if curr_path.get(path) else {}
                        curr_path = curr_path[path]
                    curr_path[key_path[-1]] = value[0] if len(value) == 1 else value
                    del record["metadata"][key]
            else:
                record["stored"] = record_hit.get("fields", dict())

        record["highlight"] = record_hit.get("highlight", dict())
        record["explanation"] = record_hit.get("_explanation", dict())

        return record
