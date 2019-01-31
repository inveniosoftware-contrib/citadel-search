#!/usr/bin/env bash

set -o errexit
set -o nounset

mkdir -p ${INVENIO_INSTANCE_PATH}
npm update && npm install --silent -g node-sass@3.8.0 clean-css@3.4.19 uglify-js@2.7.3 requirejs@2.2.0
# If set install devel, else install prod
if [ -n "${DEVEL-}" ]; then
    yum install -y git
    pip install -r requirements-devel.txt
else
    pip install -r requirements.txt
fi
pip install -e .[all,postgresql,elasticsearch6]

# Needed for invenio-admin UI
invenio npm
export BACKPATH=$(pwd)
cd ${INVENIO_INSTANCE_PATH}/static
npm install
invenio collect -v
invenio assets build
mv /code/static/${LOGO_PATH} ${INVENIO_INSTANCE_PATH}/static/${LOGO_PATH}

# PID File for uWSGI
touch /code/uwsgi.pid
chmod 666 /code/uwsgi.pid
