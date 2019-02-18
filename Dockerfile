# -*- coding: utf-8 -*-

# Use CentOS7:
FROM inveniosoftware/centos7-python:3.6
ARG build_devel
ENV DEVEL=$build_devel

# Install pre-requisites
RUN yum update -y && \
    yum install -y \
        gcc \
        openssl \
        openldap-devel \
        https://linuxsoft.cern.ch/cern/centos/7/cern/x86_64/Packages/CERN-CA-certs-20180516-1.el7.cern.noarch.rpm

# CERN Search installation
WORKDIR /${WORKING_DIR}/src
ADD . /${WORKING_DIR}/src

# Install dependencies globally
RUN pipenv install --system --deploy
# If env is development, install development dependencies
RUN if [ -n "${DEVEL-}" ]; then pip install -r requirements-devel.txt; fi
# Install CSaS
RUN pip install -e .[all,postgresql,elasticsearch6]

# PID File for uWSGI
RUN touch /${WORKING_DIR}/src/uwsgi.pid
RUN chmod 666 /${WORKING_DIR}/src/uwsgi.pid

# Patch auth
RUN sh /${WORKING_DIR}/src/scripts/patch/oauth_patch.sh

# Install UI
USER invenio
RUN invenio collect -v
RUN invenio webpack buildall
# Move static files to instance folder
RUN mv /${WORKING_DIR}/src/static/images/cernsearchicon.png ${INVENIO_INSTANCE_PATH}/static/images/cernsearchicon.png

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

CMD ["/bin/sh", "-c", "uwsgi --module ${UWSGI_WSGI_MODULE} --socket 0.0.0.0:${UWSGI_PORT} --master --processes ${UWSGI_PROCESSES} --threads ${UWSGI_THREADS} --stats /tmp/stats.socket"]