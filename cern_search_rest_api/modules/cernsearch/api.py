#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record API."""
from cern_search_rest_api.modules.cernsearch.utils import default_record_to_mapping
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record

from .fetchers import recid_fetcher


class CernSearchRecord(Record):
    """CERN Search Record."""

    record_fetcher = staticmethod(recid_fetcher)

    @classmethod
    def create(cls, data, id_=None, with_bucket=True, **kwargs):
        """Create a record and the associated bucket.

        :param with_bucket: Create a bucket automatically on record creation if mapping allows
        """
        bucket_allowed = False
        mapping = default_record_to_mapping(data)
        if mapping is not None:
            bucket_allowed = '_bucket' in mapping['properties']

        return super(CernSearchRecord, cls).create(data, id_=id_, with_bucket=bucket_allowed, **kwargs)

    @property
    def pid(self):
        """Return an instance of record PID."""
        pid = self.record_fetcher(self.id, self)

        return PersistentIdentifier.get(pid.pid_type, pid.pid_value)
