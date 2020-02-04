# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for tasks."""
from io import BytesIO
from unittest import mock

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from invenio_files_rest.storage import FileStorage

READ_MODE_BINARY = 'rb'


@mock.patch.object(CernSearchRecord, '_CernSearchRecord__buckets_allowed', return_value=True)
def test_create_file_with_buckets(db, location):
    """Test record creation with both buckets."""
    record = CernSearchRecord.create({'title': 'test'})  # type: CernSearchRecord
    record = CernSearchRecord.get_record(record.id)

    assert record.bucket_id is not None
    assert record.bucket_content_id is not None

    assert record['_bucket'] == record.bucket_id
    assert record['_bucket_content'] == record.bucket_content_id


@mock.patch.object(CernSearchRecord, '_CernSearchRecord__buckets_allowed', return_value=False)
def test_create_file_without_buckets(db, location):
    """Test record creation with no buckets."""
    record = CernSearchRecord.create({'title': 'test'})  # type: CernSearchRecord
    db.session.commit()

    assert record.bucket_id == ""
    assert record.bucket_content_id == ""

    assert '_bucket' not in record
    assert '_bucket_content' not in record


@mock.patch.object(CernSearchRecord, '_CernSearchRecord__buckets_allowed', return_value=True)
def test_record_create_files(db, location):
    """Test record creation with bucket and files."""
    record = CernSearchRecord.create({'title': 'test'})

    assert 0 == len(record.files)
    assert 0 == len(record.files_content)

    file_content = b'Hello world!'
    record.files['hello.txt'] = BytesIO(file_content)
    db.session.commit()

    record = CernSearchRecord.get_record(record.id)

    assert record['_bucket'] == record.bucket_id
    assert record['_files']

    file_1 = record.files['hello.txt']
    assert 'hello.txt' == file_1['key']
    assert 1 == len(record.files)
    assert 1 == len(record['_files'])
    assert 0 == len(record.files_content)

    storage = file_1.obj.file.storage()  # type: FileStorage
    fp = storage.open(mode=READ_MODE_BINARY)

    try:
        assert file_content == fp.read()
    finally:
        fp.close()
