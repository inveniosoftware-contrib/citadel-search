# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Use CentOS7:
FROM gitlab-registry.cern.ch/webservices/cern-search/cern-search-rest-api/cern-search-rest-api-base:6c8529ea9d6817aaab9f64f4c3c55870c5b28d4f
ARG build_env

# CERN Search installation
WORKDIR /${WORKING_DIR}/src
ADD . /${WORKING_DIR}/src

# Install CSaS
# If env is development, installs also development dependencies.
RUN if [ "$build_env" != "prod" ]; \
    then poetry install --no-root --no-interaction --no-ansi && python setup.py develop --no-deps; \
    else python setup.py install --no-deps; fi

# PID File for uWSGI
RUN touch /${WORKING_DIR}/src/uwsgi.pid
RUN chmod 666 /${WORKING_DIR}/src/uwsgi.pid

ENV LOGS_DIR=/var/log
RUN mkdir -p ${LOGS_DIR}
RUN chown -R invenio:root ${LOGS_DIR}

# Tika default logs dir
ENV TIKA_LOG_PATH=${LOGS_DIR}

# Install UI
USER invenio

# Collect static files
RUN invenio collect -v
RUN cp /${WORKING_DIR}/src/static/images/cernsearchicon.png ${INVENIO_INSTANCE_PATH}/static/images/cernsearchicon.png

# Build assets
RUN invenio webpack buildall

EXPOSE 5000

# uWSGI configuration
ARG UWSGI_WSGI_MODULE=cern_search_rest_api.wsgi:application
ENV UWSGI_WSGI_MODULE ${UWSGI_WSGI_MODULE:-cern_search_rest_api.wsgi:application}
ARG UWSGI_PORT=5000
ENV UWSGI_PORT ${UWSGI_PORT:-5000}
ARG UWSGI_PROCESSES=2
ENV UWSGI_PROCESSES ${UWSGI_PROCESSES:-2}
ARG UWSGI_THREADS=2
ENV UWSGI_THREADS ${UWSGI_THREADS:-2}

CMD ["/bin/bash", "-c", "uwsgi --module ${UWSGI_WSGI_MODULE} --socket 0.0.0.0:${UWSGI_PORT} --master --processes ${UWSGI_PROCESSES} --threads ${UWSGI_THREADS} --stats /tmp/stats.socket"]
