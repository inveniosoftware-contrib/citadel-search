# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Tests for receivers."""

from unittest.mock import patch

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.receivers import (file_deleted_listener, file_processed_listener,
                                                               file_uploaded_listener, record_deleted_listener)


@patch('cern_search_rest_api.modules.cernsearch.receivers.delete_previous_record_file_if_exists')
@patch('cern_search_rest_api.modules.cernsearch.receivers.process_file_async.delay')
def test_file_uploaded_listener(
        process_file_async_mock,
        delete_previous_record_file_if_exists_mock,
        base_app,
        record_with_file
):
    """Test process file calls."""
    obj = record_with_file.files['hello.txt']
    file_uploaded_listener(obj)

    process_file_async_mock.assert_called_once_with(str(obj.bucket_id), obj.key)
    delete_previous_record_file_if_exists_mock.assert_called_once_with(obj)


@patch('cern_search_rest_api.modules.cernsearch.receivers.delete_file_instance')
@patch('cern_search_rest_api.modules.cernsearch.receivers.CernSearchRecordIndexer')
@patch('cern_search_rest_api.modules.cernsearch.receivers.persist_file_content')
@patch('cern_search_rest_api.modules.cernsearch.receivers.record_from_object_version')
def test_file_processed_listener(
        record_from_object_version_mock,
        persist_file_content_mock,
        record_indexer_mock,
        delete_file_mock,
        base_app,
        record_with_file
):
    """Test process file calls."""
    record = CernSearchRecord.get_record(record_with_file.id)
    record_from_object_version_mock.return_value = record
    file = record_with_file.files['hello.txt']
    data = dict(content='    A simple frase.     With some empty space.   ')
    file_processed_listener(
        app=base_app,
        processor_id='some-processor',
        file=file.obj,
        data=data
    )

    record_from_object_version_mock.assert_called_once_with(file.obj)
    persist_file_content_mock.assert_called_once_with(
        record,
        data,
        file.obj.basename
    )
    record_indexer_mock.assert_called_once()
    delete_file_mock.assert_called_once_with(file.obj)


@patch('cern_search_rest_api.modules.cernsearch.receivers.CernSearchRecordIndexer')
@patch('cern_search_rest_api.modules.cernsearch.receivers.delete_record_file')
@patch('cern_search_rest_api.modules.cernsearch.receivers.record_from_object_version')
def test_file_deleted_listener(
        record_from_object_version_mock,
        delete_record_file_mock,
        record_indexer_mock,
        base_app,
        record_with_file
):
    """Test process file calls."""
    record = CernSearchRecord.get_record(record_with_file.id)
    record_from_object_version_mock.return_value = record

    obj = record_with_file.files['hello.txt']
    file_deleted_listener(obj)

    delete_record_file_mock.assert_called_once_with(obj)
    record_from_object_version_mock.assert_called_once_with(obj)
    record_indexer_mock.assert_called_once()


@patch('cern_search_rest_api.modules.cernsearch.receivers.delete_all_record_files')
def test_record_deleted_listener(
        delete_all_record_files_mock,
        base_app,
        record_with_file
):
    """Test process file calls."""
    record = CernSearchRecord.get_record(record_with_file.id)
    record_deleted_listener(sender=base_app, record=record)

    delete_all_record_files_mock.assert_called_once_with(record)
