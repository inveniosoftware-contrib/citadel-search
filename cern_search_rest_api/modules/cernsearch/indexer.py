#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Indexer utilities."""
import json as json_lib

from flask import current_app
from invenio_files_rest.storage import FileStorage
from invenio_indexer.api import RecordIndexer

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.file_meta import extract_metadata_from_processor

READ_MODE_BINARY = "rb"
READ_WRITE_MODE_BINARY = "rb+"

CONTENT_KEY = "content"
FILE_KEY = "file"
FILE_FORMAT_KEY = "file_extension"
DATA_KEY = "_data"
AUTHORS_KEY = "authors"
COLLECTION_KEY = "collection"
NAME_KEY = "name"
KEYWORDS_KEY = "keywords"
CREATION_KEY = "creation_date"
# Hard limit on content on 99.9MB due to ES limitations
# Ref: https://www.elastic.co/guide/en/elasticsearch/reference/7.1/general-recommendations.html#maximum-document-size
CONTENT_HARD_LIMIT = int(99.9 * 1024 * 1024)


class CernSearchRecordIndexer(RecordIndexer):
    """Record Indexer."""

    record_cls = CernSearchRecord


def index_file_content(
    sender,
    json=None,
    record: CernSearchRecord = None,
    index=None,
    doc_type=None,
    arguments=None,
    **kwargs,
):
    """Index file content in search."""
    if not record.files_content:
        return

    for file_obj in record.files_content:
        current_app.logger.debug("Index file content: %s in %s", file_obj.obj.basename, record.id)

        storage = file_obj.obj.file.storage()  # type: FileStorage
        with storage.open(mode=READ_WRITE_MODE_BINARY) as fp:
            file_content = json_lib.load(fp)
            check_file_content_limit(file_content, file_obj.obj.basename, record.id)

            json[DATA_KEY][CONTENT_KEY] = file_content["content"]
            json[FILE_KEY] = file_obj.obj.basename

            if current_app.config.get("PROCESS_FILE_META"):
                index_metadata(file_content, json, file_obj.obj.basename)

        # Index first or none
        break


def index_metadata(file_content, json, file_name):
    """Extract metadata from file to be indexed."""
    metadata = extract_metadata_from_processor(file_content["metadata"])

    if metadata.get("authors"):
        json[DATA_KEY][AUTHORS_KEY] = metadata.get("authors")
    if metadata.get("content_type"):
        json[COLLECTION_KEY] = metadata["content_type"]
    if metadata.get("title"):
        json[DATA_KEY][NAME_KEY] = metadata["title"]
    if metadata.get("keywords"):
        json[DATA_KEY][KEYWORDS_KEY] = metadata["keywords"]
    if metadata.get("creation_date"):
        json[CREATION_KEY] = metadata["creation_date"]

    if "." in file_name:
        json[FILE_FORMAT_KEY] = file_name.split(".")[-1]


def check_file_content_limit(file_content, file_name, record_id):
    """Check file content limit and truncate if necessary."""
    if len(str(file_content["content"])) > CONTENT_HARD_LIMIT:
        current_app.logger.warning("Truncated file content: %s in %s", file_name, record_id)
        file_content["content"] = str(file_content["content"])[:CONTENT_HARD_LIMIT]
