#!/usr/bin/env bash

invenio db init
invenio db create
invenio index init
invenio index queue init