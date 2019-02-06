#!/usr/bin/env bash


location=$(pipenv run pip show invenio-oauthclient | grep Location | awk '{print $2}')

rm -f ${location}/invenio_oauthclient/contrib/cern.py
cp /${WORKING_DIR}/src/scripts/patch/cern.py ${location}/invenio_oauthclient/contrib/cern.py
