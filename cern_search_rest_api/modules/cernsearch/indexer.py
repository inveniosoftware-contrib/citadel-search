#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from flask import current_app


def csas_indexer_receiver(sender, json=None, record=None, index=None,
                          doc_type=None, arguments=None, **kwargs):

    pipeline_mapping = current_app.config['SEARCH_DOC_PIPELINES']

    if pipeline_mapping:
        pipeline = pipeline_mapping.get(doc_type, None)

        if pipeline:
            arguments['pipeline'] = pipeline
