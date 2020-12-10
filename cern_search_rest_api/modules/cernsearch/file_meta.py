#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""File Meta utilities."""
import mimetypes

from cern_search_rest_api.modules.cernsearch.utils import reverse_dict_list

FILE_EXT_COLLECTIONS = {
    "Document": ["doc", "docx", "odt", "pages", "rtf", "tex", "wpd", "txt"],
    "PDF": ["pdf"],
    "Sheet": ["ods", "xlsx", "xlsm", "xls", "numbers"],
    "Slides": ["ppt", "pptx", "pps", "odp", "key"],
}

FILE_EXT_DEFAULT_COLLECTION = "Other"

FILE_EXTENSION_MAP = reverse_dict_list(FILE_EXT_COLLECTIONS)


def extract_metadata_from_processor(metadata):
    """Prepare metadata from processor."""
    extracted = {}

    if metadata.get("Author"):
        authors = metadata["Author"]
        extracted["authors"] = authors.strip(" ") if isinstance(authors, str) else ", ".join(authors)
    if metadata.get("Content-Type"):
        extracted["content_type"] = mime_type_to_file_collection(metadata["Content-Type"])
    if metadata.get("title"):
        extracted["title"] = metadata["title"]
    if metadata.get("Keywords"):
        keywords = metadata["Keywords"]
        if not isinstance(keywords, list):
            keywords = keywords.split(",")

        # strip
        keywords = [keyword.strip(" ") for keyword in keywords]
        extracted["keywords"] = keywords
    if metadata.get("Creation-Date"):
        extracted["creation_date"] = metadata["Creation-Date"]

    return extracted


def mime_type_to_file_collection(mime_type):
    """Convert mime type to a friendly name collection."""
    extensions = mimetypes.guess_all_extensions(mime_type.split(";")[0], strict=False)
    if not extensions:
        return FILE_EXT_DEFAULT_COLLECTION

    def strip_dot(extension):
        return extension.strip(".")

    for ext in extensions:
        collection = FILE_EXTENSION_MAP.get(strip_dot(ext))
        if collection:
            return collection

    return FILE_EXT_DEFAULT_COLLECTION
