#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Citadel Search."""

import os

from setuptools import setup

readme = open("README.md").read()
history = open("CHANGES.md").read()

setup_requires = [
    "pytest-runner>=3.0.0,<5",
]

tests_require = [
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "pytest",
]

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("cern_search_rest_api", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="cern-search-rest-api",
    version=version,
    description="CERN Search as a Service",
    long_description=readme + "\n\n" + history,
    license="GPLv3",
    author="CERN",
    author_email="cernsearch.support@cern.ch",
    url="http://search.cern.ch/",
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": [
            "cern_search_rest_api = invenio_app.cli:cli",
        ],
        "invenio_config.module": ["cern_search_rest_api = cern_search_rest_api.config"],
        "invenio_search.mappings": [
            "test = cern_search_rest_api.modules.cernsearch.mappings.test",
            "indico = cern_search_rest_api.modules.cernsearch.mappings.indico",
            "webservices = cern_search_rest_api.modules.cernsearch.mappings.webservices",
            "edms = cern_search_rest_api.modules.cernsearch.mappings.edms",
            "archives = cern_search_rest_api.modules.cernsearch.mappings.archives",
        ],
        "invenio_jsonschemas.schemas": [
            "test = cern_search_rest_api.modules.cernsearch.jsonschemas.test",
            "indico = cern_search_rest_api.modules.cernsearch.jsonschemas.indico",
            "webservices = cern_search_rest_api.modules.cernsearch.jsonschemas.webservices",
            "edms = cern_search_rest_api.modules.cernsearch.jsonschemas.edms",
            "archives = cern_search_rest_api.modules.cernsearch.jsonschemas.archives",
        ],
        "invenio_base.apps": ["cern-search = cern_search_rest_api.modules.cernsearch.ext:CERNSearch"],
        "invenio_base.api_apps": ["cern-search = cern_search_rest_api.modules.cernsearch.ext:CERNSearch"],
        "invenio_base.blueprints": [
            "health_check = cern_search_rest_api.modules.cernsearch.views:build_health_blueprint"
        ],
        "invenio_celery.tasks": ["cern-search = cern_search_rest_api.modules.cernsearch.tasks"],
        "flask.commands": ["utils = cern_search_rest_api.modules.cernsearch.cli:utils"],
    },
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 1 - Pre-Alpha",
    ],
    setup_requires=setup_requires,
    tests_require=tests_require,
    install_requires=install_requires,
)
