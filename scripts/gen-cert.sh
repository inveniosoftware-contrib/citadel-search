#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

openssl genrsa -des3 -passout pass:x -out nginx.pass.key 2048
openssl rsa -passin pass:x -in nginx.pass.key -out nginx.key
rm nginx.pass.key
openssl req -new -key nginx.key -out nginx.csr \
  -subj "/C=CH/ST=Geneve/L=Geneve/O=CERN/OU=IT Department/CN=Search as a Service"
openssl x509 -req -days 365 -in nginx.csr -signkey nginx.key -out nginx.crt
