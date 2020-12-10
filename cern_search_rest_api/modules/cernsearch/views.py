#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Search views.

Custom UPDATE REST API for CERN Search to support _update_by_query.
Limitation: The query fails when the _version value (version_id in invenio-records) is 0 (<1).

Custom GET file api to get file content instead of real file.
"""

from __future__ import absolute_import, print_function

from copy import deepcopy
from functools import partial, wraps
from typing import Callable

from flask import Blueprint, Response, current_app, json, make_response, request, url_for
from invenio_db import db
from invenio_files_rest.serializer import json_serializer
from invenio_files_rest.views import ObjectResource
from invenio_indexer.utils import default_record_to_index
from invenio_records_files.serializer import serializer_mapping
from invenio_records_rest import current_records_rest
from invenio_records_rest.errors import InvalidDataRESTError, UnsupportedMediaRESTError
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import create_error_handlers as records_rest_error_handlers
from invenio_records_rest.views import need_record_permission, pass_record
from invenio_rest import ContentNegotiatedMethodView
from invenio_search import current_search_client
from six import iteritems
from six.moves.urllib.parse import urljoin

from cern_search_rest_api.modules.cernsearch.api import CernSearchRecord
from cern_search_rest_api.modules.cernsearch.errors import InvalidRecordFormatError
from cern_search_rest_api.modules.cernsearch.search import RecordCERNSearch


def elasticsearch_mapper_parsing_exception_handler(error):
    """Handle mapper parsing exceptions from ElasticSearch."""
    description = (
        f"The format of the record is invalid. "
        f"{error.info['error']['root_cause']}. {error.info['error']['caused_by']['reason']}"
    )
    return InvalidRecordFormatError(description=description).get_response()


def create_error_handlers(blueprint):
    """Create error handlers on blueprint."""
    records_rest_error_handlers(blueprint)


def build_url_action_for_pid(pid, action):
    """."""
    return url_for(
        "cernsearch_ubq.{0}".format(pid.pid_type),
        pid_value=pid.pid_value,
        action=action,
        _external=True,
    )


def build_blueprint_record_files_content(app):
    """Build blueprint for file content routes."""
    invenio_records_files_content = Blueprint("invenio_records_files_content", __name__, url_prefix="")

    # Files Content
    for rest_endpoint_config, rec_files_mappings in iteritems(app.config["RECORDS_FILES_REST_ENDPOINTS"]):
        for endpoint_prefix, files_path_name in iteritems(rec_files_mappings):
            if endpoint_prefix not in app.config[rest_endpoint_config]:
                raise ValueError(f"Endpoint {endpoint_prefix} is not present in {rest_endpoint_config}")

            # e.g. /api/records/<recid>
            rec_item_route = app.config[rest_endpoint_config][endpoint_prefix]["item_route"]
            # e.g. /files
            files_path_name = urljoin("/", files_path_name)

            object_view = SearchRecordObjectResource.as_view(
                endpoint_prefix + "_object_api",
                serializers={
                    "application/json": partial(
                        json_serializer,
                        view_name="{}_object_api".format(endpoint_prefix),
                        serializer_mapping=serializer_mapping,
                    )
                },
            )

            invenio_records_files_content.add_url_rule(
                "{rec_item_route}{files_path_name}/<path:key>".format(**locals()),
                view_func=object_view,
                methods=["GET"],
            )

    return invenio_records_files_content


def build_blueprint(app):
    """."""
    blueprint = Blueprint(
        "ubq",
        __name__,
        url_prefix="",
    )

    create_error_handlers(blueprint)

    endpoints = app.config.get("RECORDS_REST_ENDPOINTS", [])
    pid_type = "docid"
    endpoint = "ubq"
    options = endpoints.get(pid_type, {})
    if options:
        options = deepcopy(options)
        # Note that the '/api/' part is added transparently since this is an api_blueprint
        options["list_route"] = "/{endpoint}/bulk/".format(endpoint=endpoint)
        options["item_route"] = "/{endpoint}/<pid(recid):pid_value>".format(endpoint=endpoint)

        update_permission_factory = obj_or_import_string(options["update_permission_factory_imp"])

        search_class = obj_or_import_string(options["search_class"], default=RecordCERNSearch)

        search_class_kwargs = {}
        if options.get("search_index"):
            search_class_kwargs["index"] = options["search_index"]

        if options.get("search_type"):
            search_class_kwargs["doc_type"] = options["search_type"]

        if search_class_kwargs:
            search_class = partial(search_class, **search_class_kwargs)

        links_factory = obj_or_import_string(options["links_factory_imp"])

        record_loaders = None
        if options.get("record_loaders"):
            record_loaders = {mime: obj_or_import_string(func) for mime, func in options["record_loaders"].items()}

        record_serializers = None
        if options.get("record_serializers"):
            record_serializers = {
                mime: obj_or_import_string(func) for mime, func in options["record_serializers"].items()
            }

        # UBQRecord
        ubq_view = UBQRecordResource.as_view(
            UBQRecordResource.view_name.format(pid_type),
            update_permission_factory=update_permission_factory,
            default_media_type=options["default_media_type"],
            search_class=search_class,
            loaders=record_loaders,
            links_factory=links_factory,
            record_serializers=record_serializers,
        )

        blueprint.add_url_rule(
            options["item_route"],
            view_func=ubq_view,
            methods=["PUT"],
        )

    return blueprint


def pass_bucket_content_id(f: Callable):
    """Decorate to retrieve a bucket."""

    @wraps(f)
    def decorate(*args, **kwargs):
        current_app.logger.debug("decorate %s", getattr(kwargs["record"], "bucket_content_id", ""))

        """Get the bucket id from the record and pass it as kwarg."""
        kwargs["bucket_id"] = getattr(kwargs["record"], "bucket_content_id", "")

        return f(*args, **kwargs)

    return decorate


class SearchRecordObjectResource(ObjectResource):
    """RecordObject item resource."""

    @pass_record
    @pass_bucket_content_id
    def get(self, pid: int, record: CernSearchRecord, **kwargs):
        """Get object or list parts of a multpart upload.

        :param pid: The pid value of the record to get the content bucket from.
        :param record: The record.
        :kwargs: contains all the parameters used by the ObjectResource view in Invenio-Files-Rest
        :returns: A Flask response.
        """
        return super(SearchRecordObjectResource, self).get(**kwargs)


class UBQRecordResource(ContentNegotiatedMethodView):
    """Resource for _update_by_query items."""

    view_name = "{0}_item"

    def __init__(
        self,
        update_permission_factory=None,
        default_media_type=None,
        search_class=None,
        record_loaders=None,
        links_factory=None,
        record_serializers=None,
        **kwargs,
    ):
        """Initialize the resource."""
        super(UBQRecordResource, self).__init__(
            method_serializers={
                "PUT": record_serializers,
            },
            default_method_media_type={"PUT": default_media_type},
            default_media_type=default_media_type,
        )
        self.update_permission_factory = update_permission_factory
        self.search_class = search_class
        self.loaders = record_loaders or current_records_rest.loaders
        self.links_factory = links_factory

    @pass_record
    @need_record_permission("update_permission_factory")
    def put(self, pid, record):
        """Update by query endpoint."""
        if request.mimetype not in self.loaders:
            raise UnsupportedMediaRESTError(request.mimetype)

        data = self.loaders[request.mimetype]()
        if data is None:
            raise InvalidDataRESTError()

        # Make query with record 'control_number'
        self.check_etag(str(record.revision_id))

        # Perform ES API _updated_by_query
        control_num_query = 'control_number:"{recid}"'.format(recid=record["control_number"])
        script = data["ubq"]
        index, doc = default_record_to_index(data)

        es_response = current_search_client.update_by_query(index=index, q=control_num_query, doc_type=doc, body=script)

        # Check that the query has only updated one record
        if es_response["updated"] == 1 and es_response["updated"] == es_response["total"]:
            # Get record from ES
            search_obj = self.search_class()
            search = search_obj.get_record(str(record.id))
            # Execute search
            search_result = search.execute().to_dict()

            if search_result["hits"]["total"] == 1:
                # Update record in DB
                record.clear()
                record.update(search_result["hits"]["hits"][0]["_source"])
                record.commit()
                db.session.commit()
                # Close DB session

                # Return success
                return self.make_response(pid, record, links_factory=self.links_factory)

        # If more than one record was updated return error and the querystring
        # so the user can handle the issue
        return make_response(
            (
                json.dumps(
                    {
                        "message": "Something went wrong, the provided script might have caused inconsistency."
                        "More than one value was updated or the amount of updated values do not "
                        "match the total modified",
                        "elasticsearch_response": es_response,
                    }
                ),
                503,
            )
        )


"""
This endpoint might lead to inconsistencies between DB and ES, use at your own risk.
Prefered options are to handle relationships at application level or perform DELETE-POST operations.
The list operation over _update_by_query might have an impact on performance since it is a heavy operation.
"""


class UBQRecordListResource(ContentNegotiatedMethodView):
    """Resource for _update_by_query items."""

    view_name = "{0}_list_item"

    def __init__(
        self,
        update_permission_factory=None,
        default_media_type=None,
        search_class=None,
        **kwargs,
    ):
        """Initialize the resource."""
        super(UBQRecordListResource, self).__init__(
            default_method_media_type={"PUT": default_media_type},
            default_media_type=default_media_type,
            **kwargs,
        )

        # TODO: check ownership?
        self.update_permission_factory = update_permission_factory

    @need_record_permission("update_permission_factory")
    def put(self):
        """Update by query endpoint."""
        # Make query to get all records

        # Get DB session

        # Perform ES API _updated_by_query

        # Check that the query updated the same amount of records than the ones in the query
        # (or less, if update is not needed)

        # If more than the specified amount of records was updated return error and the query string
        # so the user can handle the issue

        # Get records from ES

        # Update records in DB

        # Close DB session

        # Return success
        return Response(
            json.dumps({"status": 200}),
            mimetype="application/json",
        )


def build_health_blueprint(app):
    """Build blueprint for health routes."""
    blueprint = Blueprint("health_check", __name__)

    @blueprint.route("/health/uwsgi")
    def uwsgi():
        """Load balancer ping view."""
        return "OK"

    @blueprint.route("/health/elasticsearch")
    def elasticsearch():
        """Load balancer ping view."""
        if current_search_client.ping():
            return "OK"
        else:
            current_app.logger.error("Health Check: Elasticsearch connection is not available")
            return make_response((json.dumps({"Elasticsearch is unavailable"}), 503))

    @blueprint.route("/health/database")
    def database():
        """Load balancer ping view."""
        if db.engine.execute("SELECT 1;").scalar() == 1:
            return "OK"
        else:
            current_app.logger.error("Health Check: Database connection is not available")
            return make_response((json.dumps({"Database connection is unavailable"}), 503))

    # Allow HTTP connections
    uwsgi.talisman_view_options = {"force_https": False}
    elasticsearch.talisman_view_options = {"force_https": False}
    database.talisman_view_options = {"force_https": False}

    return blueprint
