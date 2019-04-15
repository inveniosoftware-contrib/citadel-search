#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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