#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Indexer utilities."""
from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from flask import current_app
from invenio_files_rest.storage import FileStorage

READ_MODE_BINARY = 'rb'
ATTACHMENT_KEY = '_attachment'
FILE_KEY = '_file'
DATA_KEY = '_data'


def index_file_content(sender, json=None, record: CernSearchRecord = None, index=None, doc_type=None,
                       arguments=None, **kwargs):
    """Index file content in search."""
    for file_obj in record.files_content:
        current_app.logger.debug(f"Index file content {file_obj.obj.basename} in {record.id}")

        storage = file_obj.obj.file.storage()  # type: FileStorage
        fp = storage.open(mode=READ_MODE_BINARY)

        try:
            file_content = fp.read()
            json[DATA_KEY][ATTACHMENT_KEY] = dict(_content=file_content)
            json[FILE_KEY] = file_obj.obj.basename
        finally:
            fp.close()

        # Index first or none
        break
