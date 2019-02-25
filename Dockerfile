# -*- coding: utf-8 -*-

# Use CentOS7:
FROM gitlab-registry.cern.ch/webservices/cern-search/cern-search-rest-api/cern-search-rest-api-base:d1f96a1c3600a9a00e76433b593d0edc0a49e532
ARG build_devel
ENV DEVEL=$build_devel

# CERN Search installation
WORKDIR /${WORKING_DIR}/src
ADD . /${WORKING_DIR}/src

# If env is development, install development dependencies
RUN if [ -n "${DEVEL-}" ]; then pip install -r requirements-devel.txt; fi

# Install CSaS
RUN pip install -e .

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