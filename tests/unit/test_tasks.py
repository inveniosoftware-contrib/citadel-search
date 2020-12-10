# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Tests for tasks."""

from unittest.mock import patch

from celery.exceptions import MaxRetriesExceededError, Reject, Retry
from invenio_files_processor.processors.tika.unpack import UnpackProcessor
from pytest import raises

from cern_search_rest_api.modules.cernsearch.tasks import process_file_async


class TestProcessFileAsync:
    """Test process file async."""

    @patch("cern_search_rest_api.modules.cernsearch.tasks.current_processors.get_processor")
    @patch("cern_search_rest_api.modules.cernsearch.tasks.ObjectVersion.get")
    def test_process_file_async_success(self, object_version_get_mock, get_processor_mock, appctx, object_version):
        """Test process file calls."""
        get_processor_mock.return_value.process.return_value = "Processed"
        object_version_get_mock.return_value = object_version

        process_file_async("00000000-0000-0000-0000-000000000000", "test.pdf")

        object_version_get_mock.assert_called_once_with("00000000-0000-0000-0000-000000000000", "test.pdf")
        get_processor_mock.assert_called_once_with(name=UnpackProcessor.id)
        get_processor_mock.return_value.process.assert_called_once_with(object_version)

    @patch(
        "cern_search_rest_api.modules.cernsearch.tasks.ObjectVersion.get",
        side_effect=Exception(),
    )
    @patch(
        "cern_search_rest_api.modules.cernsearch.tasks.process_file_async.retry",
        side_effect=Retry(),
    )
    def test_process_file_async_retry(self, process_file_async_retry, object_version_get_mock, object_version):
        """Test process file calls."""
        with raises(Retry):
            process_file_async("00000000-0000-0000-0000-000000000000", "test.pdf")

    @patch(
        "cern_search_rest_api.modules.cernsearch.tasks.ObjectVersion.get",
        side_effect=Exception(),
    )
    @patch(
        "cern_search_rest_api.modules.cernsearch.tasks.process_file_async.retry",
        side_effect=MaxRetriesExceededError(),
    )
    def test_process_file_async_failure(self, process_file_async_retry_mock, object_version):
        """Test process file calls."""
        with raises(Reject):
            process_file_async("00000000-0000-0000-0000-000000000000", "test.pdf")
