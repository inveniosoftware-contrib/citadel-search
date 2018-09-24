# -*- coding: utf-8 -*-

# Use CentOS7:
FROM cern/cc7-base

# Install pre-requisites
RUN yum update -y && \
    yum install -y epel-release && \
    yum install -y \
        python-devel \
        python-pip \
        gcc \
        openssl \
        npm \
        openldap-devel && \
    pip install --upgrade pip setuptools wheel

ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# For PoC purposes
ENV FLASK_DEBUG=1

# CERN Search installation
WORKDIR /code
ADD . /code

ENV INVENIO_INSTANCE_PATH=/usr/local/var/cernsearch/var/cernsearch-instance
ENV LOGO_PATH=/images/cernsearchicon.png

RUN chmod g=u /etc/passwd && \
    chmod +x /code/scripts/*.sh && \
    sh /code/scripts/create-instance.sh && \
    sh /code/scripts/gen-cert.sh && \
    chmod +x /code/scripts/patch/oauth_patch.sh && \
    sh /code/scripts/patch/oauth_patch.sh && \
    mv nginx.crt nginx.key ${INVENIO_INSTANCE_PATH} && \
    chgrp -R 0 ${INVENIO_INSTANCE_PATH} && \
    chmod -R g=u ${INVENIO_INSTANCE_PATH} &&\
    adduser --uid 1000 invenio --gid 0 && \
    chown -R invenio:root /code

# uWSGI configuration
ARG UWSGI_WSGI_MODULE=cern_search_rest_api.wsgi:application
ENV UWSGI_WSGI_MODULE ${UWSGI_WSGI_MODULE:-cern_search_rest_api.wsgi:application}
ARG UWSGI_PORT=5000
ENV UWSGI_PORT ${UWSGI_PORT:-5000}
ARG UWSGI_PROCESSES=2
ENV UWSGI_PROCESSES ${UWSGI_PROCESSES:-2}
ARG UWSGI_THREADS=2
ENV UWSGI_THREADS ${UWSGI_THREADS:-2}

USER 1000

EXPOSE 5000

CMD ["/bin/sh", "-c", "/code/scripts/manage-user.sh && uwsgi --module ${UWSGI_WSGI_MODULE} --socket 0.0.0.0:${UWSGI_PORT} --master --processes ${UWSGI_PROCESSES} --threads ${UWSGI_THREADS} --stats /tmp/stats.socket"]