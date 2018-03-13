#!/usr/bin/env bash

set -o errexit
set -o nounset

mkdir -p ${INVENIO_INSTANCE_PATH}
pip install -r requirements.txt
pip install -e .[all,postgresql,elasticsearch5]
