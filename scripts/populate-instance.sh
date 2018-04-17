#!/usr/bin/env bash

invenio db init
invenio db create
invenio index init
invenio collect
export BACKPATH=$(pwd)
cd ${INVENIO_APP_ALLOWED_HOSTS}/static
npm install
cd ${BACKPATH}
invenio assets build