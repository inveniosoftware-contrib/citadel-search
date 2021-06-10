#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Signal Receivers."""
from flask import current_app
from invenio_files_rest.models import ObjectVersion

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.files import (
    delete_all_record_files,
    delete_file_instance,
    delete_previous_record_file_if_exists,
    delete_record_file,
    persist_file_content,
    record_from_object_version,
)
from cern_search_rest_api.modules.cernsearch.indexer import CernSearchRecordIndexer
from cern_search_rest_api.modules.cernsearch.tasks import process_file_async


def file_uploaded_listener(obj: ObjectVersion = None):
    """Process file function calls file processor async."""
    current_app.logger.debug("File uploaded listener: %s", str(obj))

    delete_previous_record_file_if_exists(obj)
    process_file_async.delay(str(obj.bucket_id), obj.key)


def file_processed_listener(app, processor_id, file: ObjectVersion, data):
    """Finish file processing.

    1. Persist extracted content
    2. Index extracted content
    3. Delete record file.
    """
    current_app.logger.debug("File processed listener: %s with processor %s", str(file), processor_id)

    file_content = __extract_content(data)
    if current_app.debug:
        for key in file_content:
            if key == "content":
                current_app.logger.debug("File processed listener: has content %s ", bool(file_content[key]))
            else:
                current_app.logger.debug("File processed listener: %s - %s ", key, file_content[key])

    record = record_from_object_version(file)
    persist_file_content(record, file_content, file.basename)
    CernSearchRecordIndexer().index(record)
    # delete real file from filesystem only after indexing successfully
    delete_file_instance(file)


def file_deleted_listener(obj: ObjectVersion = None):
    """File deleted through api calls: cleanup files and reindex."""
    current_app.logger.debug("File deleted listener: %s", str(obj))

    record = record_from_object_version(obj)

    delete_record_file(record, obj)
    CernSearchRecordIndexer().index(record)


def record_deleted_listener(sender, record: CernSearchRecord, *args, **kwargs):
    """Record deleted through api calls: cleanup files."""
    current_app.logger.debug("File deleted listener: %s", str(record))
    delete_all_record_files(record)


def __extract_content(data: dict):
    return data
