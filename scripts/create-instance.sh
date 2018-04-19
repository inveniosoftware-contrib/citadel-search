#!/usr/bin/env bash

set -o errexit
set -o nounset

mkdir -p ${INVENIO_INSTANCE_PATH}
npm update && npm install --silent -g node-sass@3.8.0 clean-css@3.4.19 uglify-js@2.7.3 requirejs@2.2.0
pip install -r requirements.txt
pip install -e .[all,postgresql,elasticsearch5]

invenio npm
export BACKPATH=$(pwd)
cd ${INVENIO_INSTANCE_PATH}/static
npm install
invenio collect -v
invenio assets build
