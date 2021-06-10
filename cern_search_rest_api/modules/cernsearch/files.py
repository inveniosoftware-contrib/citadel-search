#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""File utilities."""
import json
from io import BytesIO

from flask import current_app
from invenio_db import db
from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_records_files.api import FileObject, FilesIterator
from invenio_records_files.models import RecordsBuckets

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord


def record_from_object_version(obj: ObjectVersion):
    """Retrieve Record given an ObjectVersion."""
    record_bucket = RecordsBuckets.query.filter_by(bucket_id=obj.bucket_id).one_or_none()

    current_app.logger.debug("Record Bucket: %s", str(record_bucket))

    record = CernSearchRecord.get_record(record_bucket.record_id)

    current_app.logger.debug("Record: %s", record.id)

    return record


def persist_file_content(record: CernSearchRecord, file_content: dict, filename: str):
    """Persist file's extracted content in bucket on filesystem and database."""
    current_app.logger.debug("Persist file: %s in record %s", filename, record.id)

    file_content.pop("attachments", None)

    bucket_content = record.files_content.bucket
    ObjectVersion.create(bucket_content, filename, stream=BytesIO(json.dumps(file_content).encode()))
    db.session.commit()


def delete_previous_record_file_if_exists(obj: ObjectVersion):
    """Delete all previous associated files to record if existing, since only one file per record is allowed."""
    record = record_from_object_version(obj)  # type: CernSearchRecord
    current_app.logger.debug("Delete previous files: %s", str(obj))

    current_app.logger.debug("Delete previous file")
    __delete_all_files_except(record.files, obj)

    current_app.logger.debug("Delete previous file content")
    __delete_all_files_except(record.files_content, obj)


def delete_object_version(obj: ObjectVersion):
    """Delete file on filesystem and soft delete on database."""
    if obj.deleted:
        return

    current_app.logger.debug("Delete Object Version: %s", str(obj))

    #  Soft delete bucket
    obj.delete(obj.bucket, obj.key)

    delete_file_instance(obj)

    db.session.commit()


def delete_file_instance(obj: ObjectVersion):
    """Delete file on filesystem and mark as not readable."""
    if obj.deleted:
        return

    f = FileInstance.get(str(obj.file_id))  # type: FileInstance
    if not f.readable:
        return

    current_app.logger.debug("Delete file instance: object %s - file %s", str(obj), str(f))
    # Mark file not readable
    f.readable = False
    db.session.commit()

    # Remove the file on disk
    # This leaves the possibility of having a file on disk dangling in case the database removal works,
    # and the disk file removal doesn't work.
    f.storage().delete()


def delete_record_file(record: CernSearchRecord, obj: ObjectVersion):
    """Delete associated file to record."""
    current_app.logger.debug("Delete file: %s", str(obj))

    delete_object_version(obj)
    if obj.key in record.files_content:
        delete_object_version(record.files_content[obj.key])


def delete_all_record_files(record: CernSearchRecord):
    """Delete all associated files to record."""
    current_app.logger.debug("Delete all record files: %s", str(record))

    __delete_all_files(record.files)
    __delete_all_files(record.files_content)


def __delete_all_files(objects: FilesIterator):
    for file in objects:  # type: FileObject
        delete_object_version(file.obj)


def __delete_all_files_except(objects: FilesIterator, obj: ObjectVersion):
    for file in objects:  # type: FileObject
        file_obj = file.obj  # type: ObjectVersion

        if not file_obj.is_head or file_obj.deleted:
            continue

        # delete previous file object versions with same name
        if file_obj.key == obj.key:
            __delete_object_versions_except(obj, objects.bucket)

            continue

        # if file has different name, delete all version
        delete_object_version(file_obj)


def __delete_object_versions_except(obj: ObjectVersion, bucket: Bucket):
    versions = ObjectVersion.get_versions(bucket, obj.key)
    for version in versions:
        if version.version_id != obj.version_id:
            delete_file_instance(version)
