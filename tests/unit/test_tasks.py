# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Tests for tasks."""

from unittest.mock import patch

from celery.exceptions import MaxRetriesExceededError, Reject, Retry
from cern_search_rest_api.modules.cernsearch.tasks import process_file_async
from pytest import raises


class TestProcessFileAsync:
    """Test process file async."""

    @patch('invenio_files_rest.models.ObjectVersion.get')
    def test_process_file_async_success(self, object_version_get, objects):
        """Test process file calls."""
        process_file_async('00000000-0000-0000-0000-000000000000', 'test.pdf')

        object_version_get.assert_called_with('00000000-0000-0000-0000-000000000000', 'test.pdf')

    @patch('invenio_files_rest.models.ObjectVersion.get', side_effect=Exception())
    @patch('cern_search_rest_api.modules.cernsearch.tasks.process_file_async.retry', side_effect=Retry())
    def test_process_file_async_retry(self, process_file_async_retry, object_version_get, objects):
        """Test process file calls."""
        with raises(Retry):
            process_file_async('00000000-0000-0000-0000-000000000000', 'test.pdf')

    @patch('invenio_files_rest.models.ObjectVersion.get', side_effect=Exception())
    @patch('cern_search_rest_api.modules.cernsearch.tasks.process_file_async.retry',
           side_effect=MaxRetriesExceededError())
    def test_process_file_async_failure(self, process_file_async_retry, objects):
        """Test process file calls."""
        with raises(Reject):
            process_file_async('00000000-0000-0000-0000-000000000000', 'test.pdf')
