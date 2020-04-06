#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Mixin helper class for preprocessing records and search results."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.base import PreprocessorMixin


class CernPreprocessorMixin(PreprocessorMixin):
    """Base class for serializers."""

    @staticmethod
    def preprocess_search_hit(pid, record_hit, links_factory=None, **kwargs):
        """Prepare a record hit from Elasticsearch for serialization."""
        record = super(CernPreprocessorMixin, CernPreprocessorMixin).preprocess_search_hit(
            pid,
            record_hit,
            links_factory=None,
            **kwargs
        )

        record["highlight"] = record_hit.get('highlight', dict())
        record["explanation"] = record_hit.get('_explanation', dict())

        return record
