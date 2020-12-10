#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

readonly SCRIPT_PATH=$(dirname $0)
readonly TLS_DIR="$SCRIPT_PATH/../nginx/tls"
readonly SSL_DIR="$SCRIPT_PATH/../nginx"

readonly KEY="tls.key"
readonly CRT="tls.crt"

mkdir -p $TLS_DIR

readonly NAME="cern.ch" # Use your own domain name


######################
# Check certificate already exists
######################

if test -f "$TLS_DIR/$NAME.crt"; then
    echo "Skipping... $NAME.crt already exists."
    exit 0;
fi

######################
# Become a Certificate Authority
######################

# Generate private key
openssl genrsa -out "$TLS_DIR/myCernRootCA.key" 2048
# Generate root certificate
openssl req -x509 -new -nodes -key "$TLS_DIR/myCernRootCA.key" -sha256 -days 825 -out "$TLS_DIR/myCernRootCA.pem" \
    -subj "/C=CH/ST=Geneve/O=CERN/CN=cern.ch"


######################
# Create CA-signed certs
######################

# Generate a private key
openssl genrsa -out "$TLS_DIR/$NAME.key" 2048
# Create a certificate-signing request
openssl req -new -sha256 \
    -key "$TLS_DIR/$NAME.key" \
    -subj "/C=CH/ST=Geneve/O=CERN/CN=cern.ch" \
    -config "$SSL_DIR/ssl.conf" \
    -out "$TLS_DIR/$NAME.csr"


# Create the signed certificate
openssl x509 -req -in "$TLS_DIR/$NAME.csr" -CA "$TLS_DIR/myCernRootCA.pem" -CAkey "$TLS_DIR/myCernRootCA.key" \
-CAserial "$TLS_DIR/$NAME.srl" -CAcreateserial \
-extfile "$SSL_DIR/ssl.conf" -extensions req_ext \
-out "$TLS_DIR/$NAME.crt" -days 3650 -sha256
