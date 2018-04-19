#!/usr/bin/env bash

openssl genrsa -des3 -passout pass:x -out wsgi.pass.key 2048
openssl rsa -passin pass:x -in wsgi.pass.key -out wsgi.key
rm wsgi.pass.key
openssl req -new -key wsgi.key -out wsgi.csr \
  -subj "/C=CH/ST=Geneve/L=Geneve/O=CERN/OU=IT Department/CN=Search as a Service"
openssl x509 -req -days 365 -in wsgi.csr -signkey wsgi.key -out wsgi.crt
