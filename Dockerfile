# -*- coding: utf-8 -*-

# Use CentOS7:
FROM cern/cc7-base

# Install pre-requisites
RUN yum update -y && \
    yum install -y epel-release && \
    yum install -y \
        python-devel \
        python-pip \
        gcc && \
    pip install --upgrade pip setuptools wheel

# For PoC purposes
ENV FLASK_DEBUG=1

# CERN Search installation
WORKDIR /code
ADD . /code

RUN chmod +x /code/scripts/create-instance.sh && \
    sh /code/scripts/create-instance.sh && \
    adduser --uid 1000 invenio --gid 0 && \
    chown -R invenio:root /code

USER 1000

ENTRYPOINT invenio
CMD run
