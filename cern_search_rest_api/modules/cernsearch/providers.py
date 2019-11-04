#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import requests
from flask import current_app
from invenio_pidstore.errors import PersistentIdentifierError
from invenio_pidstore.models import PIDStatus, RecordIdentifier
from invenio_pidstore.providers.base import BaseProvider


class CERNSearchRecordIdProvider(BaseProvider):
    """Record identifier provider."""

    pid_type = 'recid'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.
    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.RESERVED
    """Record IDs are by default registered immediately."""

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier."""
        # Request next integer in recid sequence.
        assert 'pid_value' not in kwargs

        provider_url = current_app.config.get('RECORDS_ID_PROVIDER_ENDPOINT',
                                              None)
        if not provider_url:
            # Don't query external service in DEBUG mode
            kwargs['pid_value'] = str(RecordIdentifier.next())
        else:
            response = requests.get(
                provider_url, headers={'User-Agent': 'cernsearch'})

            if not response.ok or response.text.strip().startswith('[ERROR]'):
                raise PersistentIdentifierError(response.text)

            kwargs['pid_value'] = response.text

        kwargs.setdefault('status', cls.default_status)
        if object_type and object_uuid:
            kwargs['status'] = PIDStatus.REGISTERED

        return super(CERNSearchRecordIdProvider, cls).create(
            object_type=object_type, object_uuid=object_uuid, **kwargs)
