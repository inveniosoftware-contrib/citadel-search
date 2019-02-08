#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.


import os

from setuptools import find_packages, setup

readme = open('README.md').read()
history = open('CHANGES.md').read()

tests_require = []

invenio_db_version = '>=1.0.2,<1.2.0'

extras_require = {
    'postgresql': [
        'invenio-db[postgresql]' + invenio_db_version,
        ],
    'elasticsearch6': [
        'elasticsearch>=6.0.0,<6.1.0',
        'elasticsearch-dsl>=6.0.0,<6.1.0',
    ],
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': [
        'pytest>=4.1.1,<4.2.0'
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'elasticsearch6'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = []

install_requires = [
    'flask',
    'invenio-access>=1.0.0,<1.1.0',
    'invenio-admin>=1.0.0,<1.1.0',
    'invenio-accounts>=1.0.0,<1.1.0',
    'invenio-app>=1.0.0,<1.0.1',
    'invenio-base>=1.0.0,<1.1.0',
    'invenio-config>=1.0.0,<1.1.0',
    'invenio-db[postgresql,versioning]>=1.0.2,<1.1.0',
    'invenio-indexer[elasticsearch6]>=1.0.0,<1.1.0',
    'invenio-jsonschemas>=1.0.0,<1.1.0',
    'invenio-logging>=1.0.0,<1.1.0',
    'invenio-records-rest[elasticsearch6]>=1.3.0,<1.4.0',
    'invenio-records[postgresql]>=1.0.0,<1.1.0',
    'invenio-rest[cors]>=1.0.0,<1.1.0',
    'invenio-oauthclient>=1.0.0,<1.1.0',
    'invenio_oauth2server>=1.0.0,<1.1.0',
    'invenio-search[elasticsearch6]>=1.0.0,<1.1.0',
    'invenio-theme>=1.1.0,<1.2.0',
    'python-ldap>=3.1.0,<3.2.0',
    'raven>=6.9.0,<6.10.0',
    'redis>=2.10.0,<3.0.0',
    'npm>=0.1.1',
    'uWSGI>=2.0.16',
    'uwsgi-tools>=1.1.1,<1.2.0',
    'idna>=2.5,<2.7',
    'urllib3<1.23',  # Needed until invenio-search[elasticsearch] is updated to 6 (depends on central service version)
]

packages = find_packages()

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
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_config.module': [
            'cern_search_rest_api = cern_search_rest_api.config'
        ],
        'invenio_search.mappings': [
            'cernsearch-test = cern_search_rest_api.modules.cernsearch.mappings.test',
            'cernsearch-indico = cern_search_rest_api.modules.cernsearch.mappings.indico',
            'cernsearch-webservices = cern_search_rest_api.modules.cernsearch.mappings.webservices',
            'cernsearch-edms = cern_search_rest_api.modules.cernsearch.mappings.edms'
        ],
        'invenio_jsonschemas.schemas': [
            'cernsearch-test = cern_search_rest_api.modules.cernsearch.jsonschemas.test',
            'cernsearch-indico = cern_search_rest_api.modules.cernsearch.jsonschemas.indico',
            'cernsearch-webservices = cern_search_rest_api.modules.cernsearch.jsonschemas.webservices',
            'cernsearch-edms = cern_search_rest_api.modules.cernsearch.jsonschemas.edms'
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
    extras_require=extras_require,

    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
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
