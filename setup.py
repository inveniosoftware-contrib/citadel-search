#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


import os

from setuptools import find_packages, setup

readme = open('README.md').read()
history = open('CHANGES.md').read()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("cern_search_rest_api", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name='cern-search-rest-api',
    version=version,
    description='CERN Search as a Service',
    long_description=readme + '\n\n' + history,
    license='GPLv3',
    author='CERN',
    author_email='cernsearch.support@cern.ch',
    url='http://search.cern.ch/',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_config.module': [
            'cern_search_rest_api = cern_search_rest_api.config'
        ],
        'invenio_search.mappings': [
            'test = cern_search_rest_api.modules.cernsearch.mappings.test',
            'cernsearch-indico = cern_search_rest_api.modules.cernsearch.mappings.indico',
            'webservices = cern_search_rest_api.modules.cernsearch.mappings.webservices',
            'edms = cern_search_rest_api.modules.cernsearch.mappings.edms'
        ],
        'invenio_jsonschemas.schemas': [
            'test = cern_search_rest_api.modules.cernsearch.jsonschemas.test',
            'cernsearch-indico = cern_search_rest_api.modules.cernsearch.jsonschemas.indico',
            'webservices = cern_search_rest_api.modules.cernsearch.jsonschemas.webservices',
            'edms = cern_search_rest_api.modules.cernsearch.jsonschemas.edms'
        ],
        'invenio_base.apps': [
            'cern-search = cern_search_rest_api.modules.cernsearch.ext:CERNSearch'
        ],
        'invenio_base.api_apps': [
            'cern-search = cern_search_rest_api.modules.cernsearch.ext:CERNSearch'
        ],
        'invenio_base.blueprints': [
            'health_check = cern_search_rest_api.modules.cernsearch.views:build_health_blueprint'
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 1 - Pre-Alpha',
    ],
)
