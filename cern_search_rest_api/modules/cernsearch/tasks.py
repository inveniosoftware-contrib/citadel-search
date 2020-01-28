#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Background Tasks."""
from flask import current_app

from celery import shared_task
from celery.app.task import Context
from celery.exceptions import MaxRetriesExceededError, Reject
from invenio_files_rest.models import ObjectVersion


@shared_task(
    bind=True,
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=3,
    default_retry_delay=60
)
def process_file_async(self, bucket_id, key_id):
    try:
        current_app.logger.debug(f"Processing file {bucket_id}:{key_id}")

        f = ObjectVersion.get(bucket_id, key_id)  # type: ObjectVersion

        ctx = self.request  # type: Context
        current_app.logger.debug(str(ctx))

        raise Exception("testing deadletter")
    except Exception:
        try:
            raise self.retry()
        except MaxRetriesExceededError as e:
            raise Reject(str(e), requeue=False)
