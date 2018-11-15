#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Persistent identifier fetcher."""

from invenio_pidstore.fetchers import FetchedPID
from .providers import CERNSearchRecordIdProvider


def recid_fetcher(record_uuid, data):
    """Fetch PID from record."""
    return FetchedPID(
        provider=CERNSearchRecordIdProvider,
        pid_type='recid',
        pid_value=str(data['recid'])
    )