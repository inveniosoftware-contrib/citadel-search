#!/usr/bin/env bash

rm -f /usr/lib/python2.7/site-packages/invenio_oauthclient/contrib/cern.py
cp /code/scripts/patch/cern.py /usr/lib/python2.7/site-packages/invenio_oauthclient/contrib/cern.py