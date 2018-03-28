#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys

from invenio_base.app import create_app_factory
from invenio_config import create_conf_loader

from . import config

env_prefix = 'INVENIO'

conf_loader = create_conf_loader(config=config, env_prefix=env_prefix)

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
                os.path.join(sys.prefix, 'var', 'instance')

"""Path to instance folder.
Defaults to ``<virtualenv>/var/instance/``. Can be overwritten using the
environment variable ``APP_INSTANCE_PATH``.
"""

create_api = create_app_factory(
    'cern_search',
    config_loader=conf_loader,
    blueprint_entry_points=['invenio_base.api_blueprints'],
    extension_entry_points=['invenio_base.api_apps'],
    converter_entry_points=['invenio_base.api_converters'],
    instance_path=instance_path,
)