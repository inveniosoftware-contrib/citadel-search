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
from flask import current_app
from invenio_files_rest.storage import FileStorage
from invenio_indexer.api import RecordIndexer

READ_MODE_BINARY = 'rb'
ATTACHMENT_KEY = '_attachment'
FILE_KEY = '_file'
DATA_KEY = '_data'
AUTHORS_KEY = 'authors'
FILE_EXT_KEY = 'fileextension'
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
            json[DATA_KEY][ATTACHMENT_KEY] = dict(_content=file_content['content'])
            json[FILE_KEY] = file_obj.obj.basename

            if(True):
                metadata = file_content['metadata']
                if metadata.get('Author'):
                    json[DATA_KEY][AUTHORS_KEY] = metadata['Author']
                if metadata.get('Content-Type'):
                    json[FILE_EXT_KEY] = metadata['Content-Type']
                if metadata.get('title'):
                    json[DATA_KEY][NAME_KEY] = metadata['title']
                if metadata.get('Keywords'):
                    json[DATA_KEY][KEYWORDS_KEY] = metadata['Keywords']
                if metadata.get('Creation-Date'):
                    json[CREATION_KEY] = metadata['Creation-Date']
        finally:
            fp.close()

        # Index first or none
        break
