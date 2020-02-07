#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Signal Receivers."""

from cern_search_rest_api.modules.cernsearch.files import (delete_file, delete_previous_record_file_if_exists,
                                                           persist_file_content, record_from_object_version)
from cern_search_rest_api.modules.cernsearch.indexer import index_file_content
from cern_search_rest_api.modules.cernsearch.tasks import process_file_async
from flask import current_app
from invenio_files_rest.models import ObjectVersion


def file_uploaded_listener(obj: ObjectVersion = None):
    """Process file function calls file processor async."""
    current_app.logger.debug(f"File uploaded listener: {str(obj)}")

    delete_previous_record_file_if_exists(obj)
    process_file_async.delay(str(obj.bucket_id), obj.key)


def file_processed_listener(app, processor_id, file: ObjectVersion, data):
    """Finish file processing.

    1. Persist extracted content
    2. Index extracted content
    3. Delete record file.
    """
    current_app.logger.debug(f"File processed listener: {str(file)} with processor {processor_id}")

    file_content = __extract_content(data)
    record = record_from_object_version(file)

    persist_file_content(record, file_content, file.basename)
    index_file_content(record, file_content, file.basename)
    delete_file(file)


def __extract_content(data: dict):
    return " ".join(data['content'].split())
