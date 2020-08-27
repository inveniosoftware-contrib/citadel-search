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
from cern_search_rest_api.modules.cernsearch.file_meta import extract_metadata_from_processor
from flask import current_app
from invenio_files_rest.storage import FileStorage
from invenio_indexer.api import RecordIndexer

READ_MODE_BINARY = 'rb'
READ_WRITE_MODE_BINARY = 'rb+'

CONTENT_KEY = 'content'
FILE_KEY = 'file'
FILE_FORMAT_KEY = 'file_extension'
DATA_KEY = '_data'
AUTHORS_KEY = 'authors'
COLLECTION_KEY = 'collection'
NAME_KEY = 'name'
KEYWORDS_KEY = 'keywords'
CREATION_KEY = 'creation_date'
# Hard limit on content on 99.9MB due to ES limitations
# Ref: https://www.elastic.co/guide/en/elasticsearch/reference/7.1/general-recommendations.html#maximum-document-size
CONTENT_HARD_LIMIT = int(99.9 * 1024 * 1024)


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

        file_content = bc_file_content(storage)
        if len(str(file_content['content'])) > CONTENT_HARD_LIMIT:
            current_app.logger.warning(f"Truncated file content: {file_obj.obj.basename} in {record.id}")
            file_content['content'] = str(file_content['content'])[:CONTENT_HARD_LIMIT]

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

            if "." in file_obj.obj.basename:
                json[FILE_FORMAT_KEY] = file_obj.obj.basename.split(".")[-1]

        # Index first or none
        break


def bc_file_content(storage):
    """Get file content: backward compatible with files without metadata.

    Except clause and write can be removed after:
    https://its.cern.ch/jira/browse/SEARCH-84
    """
    try:
        with storage.open(mode=READ_WRITE_MODE_BINARY) as fp:
            file_content = json_lib.load(fp)
            if isinstance(file_content, dict) and 'content' in file_content:
                return file_content

            file_content = {'content': file_content}
            fp.seek(0)
            fp.write(json_lib.dumps(file_content).encode())

            return file_content
    except ValueError:
        with storage.open(mode=READ_WRITE_MODE_BINARY) as fp:
            file_content = fp.read().decode()
            file_content = {'content': file_content}

            fp.seek(0)
            fp.write(json_lib.dumps(file_content).encode())

            return file_content
