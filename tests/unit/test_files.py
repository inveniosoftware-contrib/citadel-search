# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for files."""
from unittest import mock
from unittest.mock import patch

from cern_search_rest_api.modules.cernsearch.files import persist_file_content


@patch('cern_search_rest_api.modules.cernsearch.files.db.session.commit')
@patch('cern_search_rest_api.modules.cernsearch.files.ObjectVersion.create')
def test_persist_file_content(
        object_version_create_mock,
        db_commit_mock,
        appctx,
        record_with_file
):
    """Test process file calls."""
    persist_file_content(record=record_with_file, file_content={"content": "some content"}, filename='test.pdf')

    object_version_create_mock.assert_called_once_with(
        record_with_file.files_content.bucket,
        'test.pdf',
        stream=mock.ANY
    )
    db_commit_mock.assert_called_once()
