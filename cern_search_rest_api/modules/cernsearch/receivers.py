#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Signal Receivers."""

from cern_search_rest_api.modules.cernsearch.tasks import process_file_async
from flask import current_app
from invenio_files_rest.models import ObjectVersion


def process_file(obj: ObjectVersion = None):
    """Process file function calls file processor async."""
    current_app.logger.debug(f"File uploaded {str(obj)}")

    process_file_async.delay(str(obj.bucket_id), obj.key)
