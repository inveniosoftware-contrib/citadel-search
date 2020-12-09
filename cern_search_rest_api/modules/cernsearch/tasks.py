#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Background Tasks."""

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, Reject
from flask import current_app
from invenio_files_processor.errors import InvalidProcessor
from invenio_files_processor.processors.tika.unpack import UnpackProcessor
from invenio_files_processor.proxies import current_processors
from invenio_files_rest.models import ObjectVersion


@shared_task(
    bind=True,
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_file_async(self, bucket_id, key_id):
    """Process file with processor tika."""
    try:
        current_app.logger.debug(f"Processing file {bucket_id}:{key_id}")

        obj = ObjectVersion.get(bucket_id, key_id)  # type: ObjectVersion
        processor = current_processors.get_processor(name=UnpackProcessor.id)  # type: UnpackProcessor
        processor.process(obj)

        current_app.logger.debug(f"Processed file {bucket_id}:{key_id}")
    except InvalidProcessor:
        # Because we use use reject_on_worker_lost, we need to handle occasional processed files been requeued.
        current_app.logger.debug(f"Requeued file {bucket_id}:{key_id} already processed")
    except Exception:
        try:
            raise self.retry()
        except MaxRetriesExceededError as e:
            raise Reject(str(e), requeue=False)
