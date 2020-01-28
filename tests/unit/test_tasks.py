# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for tasks."""
from cern_search_rest_api.modules.cernsearch.tasks import process_file_async
from invenio_files_rest.models import ObjectVersion


def test_process_file(appctx, objects):
    """Test Celery initialization."""
    process_file_async.delay('00000000-0000-0000-0000-000000000000', 'test.pdf')
