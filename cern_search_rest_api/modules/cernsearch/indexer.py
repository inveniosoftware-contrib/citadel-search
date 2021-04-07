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
from json import JSONDecodeError

from celery.utils.log import get_task_logger
from flask import current_app
from invenio_files_rest.storage import FileStorage
from invenio_indexer.api import RecordIndexer

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.file_meta import extract_metadata_from_processor
from cern_search_rest_api.modules.cernsearch.tasks import process_file_async

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
# Hard limit on content on 1MB due to ES limitations
# Ref: https://www.elastic.co/guide/en/elasticsearch/reference/7.1/general-recommendations.html#maximum-document-size
CONTENT_HARD_LIMIT = int(1 * 1024 * 1024)

logger = get_task_logger(__name__)


class CernSearchRecordIndexer(RecordIndexer):
    """Record Indexer."""

    record_cls = CernSearchRecord

    #
    # Add ensure connection
    #
    def _bulk_op(self, record_id_iterator, op_type, index=None, doc_type=None):
        """Index record in Elasticsearch asynchronously.

        :param record_id_iterator: Iterator that yields record UUIDs.
        :param op_type: Indexing operation (one of ``index``, ``create``,
            ``delete`` or ``update``).
        :param index: The Elasticsearch index. (Default: ``None``)
        :param doc_type: The Elasticsearch doc_type. (Default: ``None``)
        """

        def errback(exc, interval):
            current_app.logging.exception(exc)
            current_app.logging.info("Retry in %s seconds.", interval)

        with self.create_producer() as producer:
            producer.connection.ensure_connection(errback=errback, max_retries=3, timeout=5)

            for rec in record_id_iterator:
                current_app.logger.debug(rec)
                producer.publish(
                    dict(
                        id=str(rec),
                        op=op_type,
                        index=index,
                        doc_type=doc_type,
                    ),
                )


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
    if not record.files and not record.files_content:
        return

    if not record.files_content:
        file_obj = next(record.files)
        logger.warning("Not file content, retrying file: %s in %s", file_obj.obj.basename, record.id)
        process_file_async.delay(str(file_obj.obj.bucket_id), file_obj.obj.key)
        return

    for file_obj in record.files_content:
        logger.debug("Index file content: %s in %s", file_obj.obj.basename, record.id)

        json[FILE_KEY] = file_obj.obj.basename

        storage = file_obj.obj.file.storage()  # type: FileStorage
        with storage.open(mode=READ_WRITE_MODE_BINARY) as fp:
            try:
                file_content = json_lib.load(fp)
            except JSONDecodeError:
                logger.error("File content contains invalid json: %s in %s", file_obj.obj.basename, record.id)
                return

            check_file_content_limit(file_content, file_obj.obj.basename, record.id)

            json[DATA_KEY][CONTENT_KEY] = file_content["content"]

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
    file_content["content"] = file_content.get("content", "")
    if not file_content["content"]:
        logger.error("No file content: %s in %s", file_name, record_id)

    if len(str(file_content["content"])) > CONTENT_HARD_LIMIT:
        logger.warning("Truncated file content: %s in %s", file_name, record_id)
        file_content["content"] = str(file_content["content"])[:CONTENT_HARD_LIMIT]
