#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Indexer utilities."""
import json as json_lib

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.utils import extract_metadata_from_processor
from flask import current_app
from invenio_files_rest.storage import FileStorage
from invenio_indexer.api import RecordIndexer

READ_MODE_BINARY = 'rb'
CONTENT_KEY = 'content'
FILE_KEY = 'file'
DATA_KEY = '_data'
AUTHORS_KEY = 'authors'
COLLECTION_KEY = 'collection'
NAME_KEY = 'name'
KEYWORDS_KEY = 'keywords'
CREATION_KEY = 'creation_date'


class CernSearchRecordIndexer(RecordIndexer):
    """Record Indexer."""

    record_cls = CernSearchRecord


def index_file_content(sender, json=None, record: CernSearchRecord = None, index=None, doc_type=None,
                       arguments=None, **kwargs):
    """Index file content in search."""
    if not record.files_content:
        return

    for file_obj in record.files_content:
        current_app.logger.debug(f"Index file content {file_obj.obj.basename} in {record.id}")

        storage = file_obj.obj.file.storage()  # type: FileStorage
        fp = storage.open(mode=READ_MODE_BINARY)

        try:
            file_content = json_lib.load(fp)
            json[DATA_KEY][CONTENT_KEY] = file_content['content']
            json[FILE_KEY] = file_obj.obj.basename

            if current_app.config.get('PROCESS_FILE_META'):
                metadata = extract_metadata_from_processor(file_content['metadata'])

                if metadata.get('authors'):
                    json[DATA_KEY][AUTHORS_KEY] = metadata.get('authors')
                if metadata.get('content_type'):
                    json[COLLECTION_KEY] = metadata['content_type']
                if metadata.get('title'):
                    json[DATA_KEY][NAME_KEY] = metadata['title']
                if metadata.get('keywords'):
                    json[DATA_KEY][KEYWORDS_KEY] = metadata['keywords']
                if metadata.get('creation_date'):
                    json[CREATION_KEY] = metadata['creation_date']
        finally:
            fp.close()

        # Index first or none
        break
