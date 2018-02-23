#!/usr/bin/python
# -*- coding: utf-8 -*-

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