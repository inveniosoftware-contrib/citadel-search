#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

readonly SCRIPT_PATH=$(dirname $0)
readonly TLS_DIR="$SCRIPT_PATH/../nginx/tls"
readonly KEY="tls.key"
readonly CRT="tls.crt"

mkdir -p $TLS_DIR

openssl req -x509 -nodes -newkey rsa:4096 \
  -subj '/C=CH/ST=Geneve/L=Geneve/O=CERN/OU=IT Department/CN=Search as a Service' \
  -keyout "$TLS_DIR/$KEY" -out "$TLS_DIR/$CRT"
