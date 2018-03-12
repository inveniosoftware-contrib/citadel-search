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

ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# For PoC purposes
ENV FLASK_DEBUG=1

# CERN Search installation
WORKDIR /code
ADD . /code

ENV INVENIO_INSTANCE_PATH=/usr/local/var/cernsearch/var/cernsearch-instance

RUN chmod g=u /etc/passwd && \
    chmod +x /code/scripts/*.sh && \
    sh /code/scripts/create-instance.sh && \
    chgrp -R 0 ${INVENIO_INSTANCE_PATH} && \
    chmod -R g=u ${INVENIO_INSTANCE_PATH} &&\
    adduser --uid 1000 invenio --gid 0 && \
    chown -R invenio:root /code

USER 1000

ENTRYPOINT ["/code/scripts/manage-user.sh && invenio run"]