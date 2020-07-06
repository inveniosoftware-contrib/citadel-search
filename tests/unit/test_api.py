# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for tasks."""
import json
from io import BytesIO
from unittest import mock

import pytest
from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from invenio_files_rest.models import ObjectVersion
from invenio_files_rest.signals import file_uploaded
from invenio_files_rest.storage import FileStorage
from pytest import raises

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


test_record_update_file_version_cases = [
    ("Update file version, ie change content", "hello.txt", b'Hello again!'),
    ("Update file, ie send a different file", "another.pdf", b'Hello again!')
]


# TODO: migrate to integration tests
@pytest.mark.parametrize(
    "obj_name, content",
    [
        ("hello.txt", b'Hello again!'),  # Update file version, ie change content
        ("another.pdf", b'Hello again!')  # Update file, ie send a different file
    ]
)
def test_record_update_file(appctx, db, record_with_file_processed, obj_name, content):
    """Test record file updates."""
    record = CernSearchRecord.get_record(record_with_file_processed.id)
    initial_file_name = 'hello.txt'
    initial_file = record.files[initial_file_name].obj  # type: ObjectVersion
    initial_file_content = record.files_content[initial_file_name].obj  # type: ObjectVersion

    assert 1 == len(record.files)
    assert 1 == len(record.files_content)
    assert initial_file.file.readable is False
    assert initial_file.deleted is False
    assert initial_file_content.file.readable is True

    record.files[obj_name] = BytesIO(content)
    db.session.commit()

    # mimic file uploaded flow
    file_uploaded.send(record.files[obj_name].obj)

    record = CernSearchRecord.get_record(record.id)

    assert record['_bucket'] == record.bucket_id
    assert record['_bucket_content'] == record.bucket_content_id

    assert 1 == len(record.files)
    assert 1 == len(record.files_content)
    assert record.files[obj_name].obj.file.readable is False
    assert initial_file_content.file.readable is False

    # different file upload creates a delete marker
    if initial_file_name != obj_name:
        with raises(KeyError):
            record.files[initial_file_name]
        with raises(KeyError):
            record.files_content[initial_file_name]

    file_1 = record.files_content[obj_name]
    assert obj_name == file_1['key']

    storage = file_1.obj.file.storage()  # type: FileStorage
    fp = storage.open(mode=READ_MODE_BINARY)

    try:
        assert content.decode() in json.load(fp)['content']
    finally:
        fp.close()
