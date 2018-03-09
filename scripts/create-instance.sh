#!/usr/bin/env bash

set -o errexit
set -o nounset

mkdir -p ${INVENIO_INSTANCE_PATH}
pip install -r requirements.txt
pip install -e .[all,elasticsearch5]

# Needed for getpwuid() from python
# Doc https://docs.openshift.org/latest/creating_images/guidelines.html#openshift-origin-specific-guidelines
# At "Support Arbitrary User IDs"
if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  fi
fi