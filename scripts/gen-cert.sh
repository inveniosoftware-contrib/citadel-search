#!/usr/bin/env bash

openssl genrsa -des3 -passout pass:x -out nginx.pass.key 2048
openssl rsa -passin pass:x -in nginx.pass.key -out nginx.key
rm nginx.pass.key
openssl req -new -key nginx.key -out nginx.csr \
  -subj "/C=CH/ST=Geneve/L=Geneve/O=CERN/OU=IT Department/CN=Search as a Service"
openssl x509 -req -days 365 -in nginx.csr -signkey nginx.key -out nginx.crt
