# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Tests for receivers."""

from unittest.mock import patch

from cern_search_rest_api.modules.cernsearch.receivers import process_file
from invenio_files_rest.models import ObjectVersion


def test_process_file(base_app, objects):
    """Test process file calls."""
    obj = ObjectVersion.get('00000000-0000-0000-0000-000000000000', 'test.pdf')
    with patch('cern_search_rest_api.modules.cernsearch.tasks.process_file_async.delay') as process_file_async:
        process_file(obj)

        process_file_async.assert_called_with(str(obj.bucket_id), obj.key)
