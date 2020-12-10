#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier fetcher."""

from invenio_pidstore.fetchers import FetchedPID


def recid_fetcher(record_uuid, data):
    """Fetch PID from record."""
    return FetchedPID(
        pid_type="recid",
        pid_value=str(data["recid"]),
    )
