#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

from flask import current_app


def csas_indexer_receiver(sender, json=None, record=None, index=None,
                          doc_type=None, arguments=None, **kwargs):

    pipeline_mapping = current_app.config['SEARCH_DOC_PIPELINES']

    if pipeline_mapping:
        pipeline = pipeline_mapping.get(doc_type, None)

        if pipeline:
            arguments['pipeline'] = pipeline
