#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record API."""
from cern_search_rest_api.modules.cernsearch.fetchers import recid_fetcher
from cern_search_rest_api.modules.cernsearch.utils import default_record_to_mapping
from invenio_files_rest.models import Bucket
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.errors import MissingModelError
from invenio_records_files.api import FilesMixin, Record
from invenio_records_files.models import RecordsBuckets

BUCKET_KEY = '_bucket'
BUCKET_CONTENT_KEY = '_bucket_content'


class CernSearchFilesMixin(FilesMixin):
    """Metafiles for CernSearchRecord models."""

    @property
    def files_content(self):
        """Get files' extracted content iterator.

        :returns: Files iterator.
        """
        if self.model is None:
            raise MissingModelError()

        bucket_content = None
        records_buckets = RecordsBuckets.query.filter_by(record_id=self.id)
        for record_bucket in records_buckets:
            if self.get(BUCKET_CONTENT_KEY) == str(record_bucket.bucket.id):
                bucket_content = record_bucket.bucket

        return self.files_iter_cls(self, bucket=bucket_content, file_cls=self.file_cls)

    @files_content.setter
    def files_content(self, data):
        """Set files' extracted content from data."""
        current_files = self.files_content
        if current_files:
            raise RuntimeError('Can not update existing files.')
        for key in data:
            current_files[key] = data[key]

    @property
    def files(self):
        """Get files iterator.

        :returns: Files iterator.
        """
        if self.model is None:
            raise MissingModelError()

        records_buckets = RecordsBuckets.query.filter_by(record_id=self.id)
        bucket = None
        for record_bucket in records_buckets:
            if self.get(BUCKET_KEY) == str(record_bucket.bucket.id):
                bucket = record_bucket.bucket

        return self.files_iter_cls(self, bucket=bucket, file_cls=self.file_cls)


class CernSearchRecord(Record, CernSearchFilesMixin):
    """CERN Search Record.

    The record class implements a one-to-one relationship between a bucket and
    a record (to store a record's file).
    It also implements a one-to-one relationship between a bucket_content and
    a record. The purpose of this bucket is to store the result of file's content extraction.

    Both buckets are automatically created and associated with the record when the record is created
    with :py:data:`CernSearchRecord.create()`.

    The buckets id are stored in the record metadata, in the keys``_bucket`` and ``_bucket_content_id``.
    """

    record_fetcher = staticmethod(recid_fetcher)

    def __init__(self, *args, **kwargs):
        """Initialize the record."""
        self._bucket_content = None
        super(CernSearchRecord, self).__init__(*args, **kwargs)

    @staticmethod
    def __buckets_allowed(data):
        buckets_allowed = False

        mapping = default_record_to_mapping(data)
        if mapping is not None:
            buckets_allowed = '_bucket' in mapping['properties']

        return buckets_allowed

    @classmethod
    def create(cls, data, id_=None, with_bucket=False, **kwargs):
        """Create a record and the associated buckets.

         Creates buckets:
          - ``bucket`` for files
          - ``bucket_content`` for files' extracted content.

        :param with_bucket: Create both buckets automatically on record creation if mapping allows.
        """
        bucket_content = None

        bucket_allowed = with_bucket or cls.__buckets_allowed(data)
        if bucket_allowed:
            bucket_content = cls.create_bucket(data)
            if bucket_content:
                cls.dump_bucket_content(data, bucket_content)

        record = super(CernSearchRecord, cls).create(data, id_=id_, with_bucket=bucket_allowed, **kwargs)

        # Create link between record and file content bucket
        if bucket_allowed and bucket_content:
            RecordsBuckets.create(record=record.model, bucket=bucket_content)
            record._bucket_content = bucket_content

        return record

    @property
    def pid(self):
        """Return an instance of record PID."""
        pid = self.record_fetcher(self.id, self)

        return PersistentIdentifier.get(pid.pid_type, pid.pid_value)

    @classmethod
    def dump_bucket_content(cls, data, bucket):
        """Dump the file content bucket id into the record metadata..

        :param data: A dictionary of the record metadata.
        :param bucket: The created bucket for the record.
        """
        data["_bucket_content"] = str(bucket.id)

    @classmethod
    def load_bucket_content(cls, record):
        """Load the file content bucket id from the record metadata.

        :param record: A record instance.
        """
        return record.get(BUCKET_CONTENT_KEY, "")

    @property
    def bucket_content_id(self):
        """Get file content bucket id from record metadata."""
        return self.load_bucket_content(self)

    @property
    def file_content_bucket(self):
        """Get file content bucket instance."""
        if self._bucket_content is None:
            if self.bucket_content_id:
                self._bucket_content = Bucket.get(self.bucket_content_id)
        return self._bucket_content

    def delete(self, force=False):
        """Delete a record and also remove the RecordsBuckets if necessary.

        :param force: True to remove also the
            :class:`~invenio_records_files.models.RecordsBuckets` object.
        :returns: Deleted record.
        """
        if force:
            RecordsBuckets.query.filter_by(record=self.model, bucket=self.files_content.bucket).delete()
        return super(CernSearchRecord, self).delete(force)
