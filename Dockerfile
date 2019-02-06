# -*- coding: utf-8 -*-

# Use CentOS7:
FROM gitlab-registry.cern.ch/webservices/cern-search/cern-search-rest-api/invenio:py36
ARG build_devel
ENV DEVEL=$build_devel

# Install pre-requisites
RUN yum update -y && \
    yum install -y \
        gcc \
        openssl \
        openldap-devel

# Change to user invenio to install the instance
USER invenio

# CERN Search installation
WORKDIR /${WORKING_DIR}/src
ADD . /${WORKING_DIR}/src

RUN if [ -n "${DEVEL-}" ]; then pipenv install -r requirements-devel.txt; else pipenv install -r requirements.txt; fi

RUN pipenv install -e .[all,postgresql,elasticsearch6]

RUN pipenv run invenio collect -v
RUN pipenv run invenio webpack buildall
RUN mv /${WORKING_DIR}/src/static/images/cernsearchicon.png ${INVENIO_INSTANCE_PATH}/static/images/cernsearchicon.png

# PID File for uWSGI
RUN touch /${WORKING_DIR}/src/uwsgi.pid
RUN chmod 666 /${WORKING_DIR}/src/uwsgi.pid

# Patch auth
USER root
RUN chmod +x /${WORKING_DIR}/src/scripts/patch/oauth_patch.sh

USER invenio
RUN sh /${WORKING_DIR}/src/scripts/patch/oauth_patch.sh

# uWSGI configuration
ARG UWSGI_WSGI_MODULE=cern_search_rest_api.wsgi:application
ENV UWSGI_WSGI_MODULE ${UWSGI_WSGI_MODULE:-cern_search_rest_api.wsgi:application}
ARG UWSGI_PORT=5000
ENV UWSGI_PORT ${UWSGI_PORT:-5000}
ARG UWSGI_PROCESSES=2
ENV UWSGI_PROCESSES ${UWSGI_PROCESSES:-2}
ARG UWSGI_THREADS=2
ENV UWSGI_THREADS ${UWSGI_THREADS:-2}



EXPOSE 5000

CMD ["/bin/sh", "-c", "/${WORKING_DIR}/src/scripts/manage-user.sh && uwsgi --module ${UWSGI_WSGI_MODULE} --socket 0.0.0.0:${UWSGI_PORT} --master --processes ${UWSGI_PROCESSES} --threads ${UWSGI_THREADS} --stats /tmp/stats.socket"]