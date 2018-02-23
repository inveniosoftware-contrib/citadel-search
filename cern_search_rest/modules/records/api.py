#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Record API"""
from invenio_records.api import Record
from invenio_pidstore.models import PersistentIdentifier

from .fetchers import recid_fetcher


class CernSearchRecord(Record):
    """CERN Searc Record."""

    record_fetcher = staticmethod(recid_fetcher)

    @property
    def pid(self):
        """Return an instance of record PID."""
        pid = self.record_fetcher(self.id, self)
        return PersistentIdentifier.get(pid.pid_type, pid.pid_value)

    """
    @property
    def depid(self):
        # Return depid of the record.
        return PersistentIdentifier.get(
            pid_type='recid',
            pid_value=self.get('_deposit', {}).get('id')
        )
    """