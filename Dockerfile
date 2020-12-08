# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Use CentOS7:
FROM gitlab-registry.cern.ch/webservices/cern-search/cern-search-rest-api/cern-search-rest-api-base:4cc14deb49f42c505062110461b96c12cda9b377
ARG build_env

# CERN Search installation
WORKDIR /${WORKING_DIR}/src
ADD . /${WORKING_DIR}/src

RUN pip freeze

# If env is development, install development dependencies
RUN if [ "$build_env" != "prod" ]; then pipenv install --system --ignore-pipfile --deploy --dev; fi

RUN pip freeze

# Install CSaS
RUN pip install -e .

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
RUN invenio collect -v
RUN invenio webpack buildall
# Move static files to instance folder
RUN cp /${WORKING_DIR}/src/static/images/cernsearchicon.png ${INVENIO_INSTANCE_PATH}/static/images/cernsearchicon.png

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
