#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Click command-line utilities."""
import json

import click
from flask.cli import with_appcontext
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.models import RecordMetadata
from invenio_search import current_search
from invenio_search.cli import es_version_check

from cern_search_rest_api.modules.cernsearch.indexer import CernSearchRecordIndexer
from cern_search_rest_api.modules.cernsearch.indexer_tasks import process_bulk_queue


def abort_if_false(ctx, param, value):
    """Abort command is value is False."""
    if not value:
        ctx.abort()


@click.group()
def utils():
    """Misc management commands."""


@utils.command("runindex")
@click.option("--delayed", "-d", is_flag=True, help="Run indexing in background.")
@click.option(
    "--chunk_size",
    "-s",
    default=500,
    type=int,
    help="Number of docs in one chunk sent to es (default: 500)",
)
@click.option(
    "--max_chunk_bytes",
    "-b",
    default=int(99.9 * 1024 * 1024),
    type=int,
    help="The maximum size of the request in bytes (default: 100MB).",
)
@click.option(
    "--concurrency",
    "-c",
    default=1,
    type=int,
    help="Number of concurrent indexing tasks to start.",
)
@click.option(
    "--queue",
    "-q",
    type=str,
    help="Name of the celery queue used to put the tasks into.",
)
@click.option("--version-type", help="Elasticsearch version type to use.")
@click.option(
    "--raise-on-error/--skip-errors",
    default=True,
    help="Controls if Elasticsearch bulk indexing errors raise an exception.",
)
@with_appcontext
def run(
    delayed,
    chunk_size,
    max_chunk_bytes,
    concurrency,
    queue=None,
    version_type=None,
    raise_on_error=True,
):
    """Run bulk record indexing."""
    es_bulk_kwargs = {
        "raise_on_error": raise_on_error,
        "chunk_size": chunk_size,
        "max_chunk_bytes": max_chunk_bytes,
    }

    if delayed:
        celery_kwargs = {"kwargs": {"version_type": version_type, "es_bulk_kwargs": es_bulk_kwargs}}
        click.secho("Starting {0} tasks for indexing records...".format(concurrency), fg="green")
        if queue is not None:
            celery_kwargs.update({"queue": queue})
        for c in range(0, concurrency):
            process_bulk_queue.apply_async(**celery_kwargs)
    else:
        click.secho("Indexing records...", fg="green")
        CernSearchRecordIndexer(version_type=version_type).process_bulk_queue(es_bulk_kwargs=es_bulk_kwargs)


@utils.command("reindex")
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you really want to reindex all records?",
)
@click.option("-t", "--pid-type", multiple=True, required=True)
@click.option("-i", "--id", "id_list", help="List of ids.", multiple=True)
@click.option("-d", "--doc-type", required=False)
@with_appcontext
def reindex(pid_type, id_list, doc_type=None):
    """Reindex all records.

    :param pid_type: Pid type.
    :param id_list: List of ids.
    :param doc_type: Doc type
    """
    click.secho("Sending records to indexing queue ...", fg="green")

    query = id_list

    if not query:
        query = (
            PersistentIdentifier.query.filter_by(object_type="rec", status=PIDStatus.REGISTERED)
            .join(RecordMetadata, PersistentIdentifier.object_uuid == RecordMetadata.id)
            .filter(PersistentIdentifier.pid_type.in_(pid_type))
        )

        if doc_type:
            query = query.filter(RecordMetadata.json.op("->>")("$schema").contains(doc_type))

        query = (x[0] for x in query.yield_per(100).values(PersistentIdentifier.object_uuid))

    CernSearchRecordIndexer().bulk_index(query)
    click.secho('Execute "run" command to process the queue!', fg="yellow")


@utils.command("index-init")
@click.argument("index_name")
@click.option("-f", "--force", is_flag=True, default=False)
@click.option("-v", "--verbose", is_flag=True, default=False)
@with_appcontext
@es_version_check
def index_init(index_name, force, verbose):
    """Init index by its name."""
    results = list(current_search.create(index_list=[index_name], ignore_existing=force))
    if verbose:
        click.echo(json.dumps(results))
