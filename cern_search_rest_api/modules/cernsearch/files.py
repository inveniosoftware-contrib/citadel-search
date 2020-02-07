#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""File utilities."""

from io import BytesIO

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.errors import ObjectNotFoundError
from flask import current_app
from invenio_db import db
from invenio_files_rest.models import FileInstance, ObjectVersion
from invenio_records_files.api import FilesIterator
from invenio_records_files.models import RecordsBuckets


def record_from_object_version(obj: ObjectVersion):
    """Retrieve Record given an ObjectVersion."""
    record_bucket = RecordsBuckets.query.filter_by(bucket_id=obj.bucket_id).one_or_none()

    if not record_bucket:
        raise ObjectNotFoundError(f"RecordsBuckets with bucket_id {obj.bucket_id}")

    current_app.logger.debug(f"Record Bucket: {str(record_bucket)}")

    record = CernSearchRecord.get_record(record_bucket.record_id)

    if not record:
        raise ObjectNotFoundError(f"CernSearchRecord with id {record_bucket.record_id}")

    current_app.logger.debug(f"Record: {str(record)}")

    return record


def persist_file_content(record: CernSearchRecord, file_content: str, filename: str):
    """Persist file's extracted content in bucket on filesystem and database."""
    current_app.logger.debug(f"Persist file: {filename}")

    bucket_content = record.files_content.bucket
    ObjectVersion.create(bucket_content, filename, stream=BytesIO(file_content.encode()))
    db.session.commit()


def delete_previous_record_file_if_exists(obj: ObjectVersion):
    """Delete all previous associated files to record if existing, since only one file per record is allowed."""
    record = record_from_object_version(obj)  # type: CernSearchRecord
    current_app.logger.debug(f"Cleanup old files: {str(obj)}, count {len(record.files)}")

    __delete_all_files_except(record.files, obj)
    __delete_all_files_except(record.files_content, obj)
    __delete_object_versions_except(obj)


def __delete_object_versions_except(obj: ObjectVersion):
    for version in ObjectVersion.get_versions(obj.bucket, obj.key):
        if version.version_id != obj.version_id:
            delete_file(version)


def __delete_all_files_except(objects: FilesIterator, obj: ObjectVersion):
    for file in objects:
        if file.obj.version_id != obj.version_id:
            delete_file(file.obj)


def delete_file(obj: ObjectVersion):
    """Delete file on filesystem and database."""
    current_app.logger.debug(f"Delete File: {str(obj)}")

    obj.remove()

    if obj.file_id:
        # First remove FileInstance from database and commit transaction to
        # ensure integrity constraints are checked and enforced.
        f = FileInstance.get(str(obj.file_id))

        if not f:
            raise ObjectNotFoundError(f"FileInstance with id {obj.file_id}")

        f.delete()
        # Next, remove the file on disk. This leaves the possibility of having
        # a file on disk dangling in case the database removal works, and the
        # disk file removal doesn't work.
        f.storage().delete()

    db.session.commit()

    # file_deleted.send(obj)
