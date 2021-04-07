# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks to index records."""

from __future__ import absolute_import, print_function

from celery import shared_task

from .indexer import CernSearchRecordIndexer


@shared_task(ignore_result=True)
def process_bulk_queue(version_type=None, es_bulk_kwargs=None):
    """Process bulk indexing queue.

    :param str version_type: Elasticsearch version type.
    :param dict es_bulk_kwargs: Passed to
        :func:`elasticsearch:elasticsearch.helpers.bulk`.

    Note: You can start multiple versions of this task.
    """
    CernSearchRecordIndexer(version_type=version_type).process_bulk_queue(es_bulk_kwargs=es_bulk_kwargs)


@shared_task(ignore_result=True)
def index_record(record_uuid):
    """Index a single record.

    :param record_uuid: The record UUID.
    """
    CernSearchRecordIndexer().index_by_id(record_uuid)


@shared_task(ignore_result=True)
def delete_record(record_uuid):
    """Delete a single record.

    :param record_uuid: The record UUID.
    """
    CernSearchRecordIndexer().delete_by_id(record_uuid)
