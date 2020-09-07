
###################  Docker development helpful directives  ####################
#
# Usage:
# make logs                   # displays log outputs from running services
# make build-env              # build environment, create and start containers
# make env                    # build environment, load fixtures and enters shell
# make destroy-env            # stop and remove containers, networks, images, and volume
# make reload-env             # restart containers, networks, images, and volume
# make shell-env              # start bash inside service
# make root-shell-env         # start bash inside service as root
# make load-fixtures          # loads fixtures
# make populate-instance      # create database, tables and indeces
# make generate-certificates  # generate nginx certificates
# make test                   # runs tests
# make lint                   # runs linting tools

SERVICE_NAME :=  cern-search-api
WORKER_NAME :=  worker
API_TOKEN := .api_token
MODE?=full
TEST_MODE=test

ifeq ($(MODE),$(TEST_MODE))
DOCKER_FILE := docker-compose.test.yml
else
DOCKER_FILE := docker-compose.full.yml
endif

build-env:
	docker-compose -f $(DOCKER_FILE) up -d --remove-orphans
.PHONY: build-env

rebuild-env:
	docker-compose -f $(DOCKER_FILE) up -d --build --remove-orphans
.PHONY: build-env

es-setup:
	curl -XPUT "http://localhost:9200/_settings" -H 'Content-Type: application/json' -d' \
	{\
        "index": {\
            "search.slowlog.level": "trace",\
            "search.slowlog.threshold.query.trace": "0ms"\
	    }\
	}'
.PHONY: es-setup

logs:
	docker-compose -f $(DOCKER_FILE) logs -f
.PHONY: logs

populate-instance:
	docker-compose -f $(DOCKER_FILE) exec -T $(SERVICE_NAME) /bin/bash -c \
		"sh /opt/invenio/src/scripts/populate-instance.sh"
.PHONY: populate-instance

load-fixtures:
	docker-compose -f $(DOCKER_FILE) exec -T $(SERVICE_NAME) /bin/bash -c \
		"sh /opt/invenio/src/scripts/create-test-user.sh"
.PHONY: load-fixtures

destroy-env:
	docker-compose -f $(DOCKER_FILE) down --volumes
	docker-compose -f $(DOCKER_FILE) rm -f
.PHONY: destroy-env

stop-env:
	docker-compose -f $(DOCKER_FILE) down --volumes
.PHONY: stop-env

reload-env: destroy-env generate-certificates rebuild-env populate-instance es-setup load-fixtures shell-env
.PHONY: reload-env

shell-env:
	docker-compose -f $(DOCKER_FILE) exec $(SERVICE_NAME) /bin/bash
.PHONY: shell-env

shell-worker:
	docker-compose -f $(DOCKER_FILE) exec $(WORKER_NAME) /bin/bash
.PHONY: shell-worker

env-staging: generate-certificates build-env populate-instance es-setup shell-env
.PHONY: env-staging

env: generate-certificates build-env populate-instance es-setup load-fixtures shell-env
.PHONY: env

generate-certificates:
	sh scripts/gen-cert.sh
.PHONY: generate-certificates

pytest:
	docker-compose -f $(DOCKER_FILE) exec -T $(SERVICE_NAME) /bin/bash -c \
	"pytest tests -vv;"
.PHONY: pytest

ci-test: build-env pytest
.PHONY: ci-test

test: stop-env build-env pytest
.PHONY: test

lint:
	docker-compose -f $(DOCKER_FILE) exec -T $(SERVICE_NAME) /bin/bash -c \
		"echo running isort...; \
		isort -rc -c -df; \
		echo running flake8...; \
		flake8 --max-complexity 10 --ignore E501,D401"
.PHONY: lint

###################  Local development helpful directives  ####################
###################           (pipenv + docker)            ####################
#
# Usage:
# make logs                     # displays log outputs from running services
# make build-local-env          # build pipenv, create and start containers
# make check-requirements-local # check requirements
# make local-env                # build virtual environment, load fixtures and starts api
# make populate-instance-local  # create database, tables and indices
# make serve-api-local          # start serving api
# make shell-local-env          # start bash inside pipenv
# make destroy-local-env        # stop and remove containers, networks, images, and volume and pipenv
# make reload-local-env         # restart containers, networks, images, and volume and pipenv
# make load-fixtures-local      # loads fixtures
# make local-test               # runs tests
# make local-lint               # runs linting tools

PIPENV_DOTENV := .pipenv.env
PYTHON_VERSION_FILE := .python-version
PYTHON_VERSION := $(cat $(PYTHON_VERSION_FILE) | xargs)
PIPENV_DOCKER_FILE := docker-compose.yml

local-env-logs:
	docker-compose -f $(PIPENV_DOCKER_FILE) logs -f
.PHONY: local-env-logs

check-requirements-local:
	PYTHON_VERSION=$(PYTHON_VERSION) sh scripts/pipenv/requirements.sh
.PHONY: check-requirements-local

build-local-env: check-requirements-local
	docker-compose -f $(PIPENV_DOCKER_FILE) up -d --build --remove-orphans
	PIPENV_DOTENV_LOCATION=$(PIPENV_DOTENV) pipenv run sh scripts/pipenv/bootstrap
.PHONY: build-local-env

populate-instance-local:
	PIPENV_DOTENV_LOCATION=$(PIPENV_DOTENV) pipenv run sh scripts/pipenv/populate-instance.sh
.PHONY: populate-instance-local

load-fixtures-local:
	PIPENV_DOTENV_LOCATION=$(PIPENV_DOTENV) pipenv run sh scripts/create-test-user.sh
.PHONY: load-fixtures-local

serve-api-local:
	PIPENV_DOTENV_LOCATION=$(PIPENV_DOTENV) pipenv run sh scripts/pipenv/server
.PHONY: serve-api-local

local-env: build-local-env populate-instance-local serve-api-local
.PHONY: local-env

shell-local-env:
	PIPENV_DOTENV_LOCATION=$(PIPENV_DOTENV) pipenv shell
.PHONY: shell-local-env

destroy-local-env:
	docker-compose -f $(PIPENV_DOCKER_FILE) down --volumes
	docker-compose -f $(PIPENV_DOCKER_FILE) rm -f
	pipenv --rm
.PHONY: destroy-local-env

reload-local-env: destroy-local-env local-env
.PHONY: reload-local-env

local-test:
	@echo running tests...;
	pipenv run pytest tests -v;
.PHONY: local-test

local-lint:
	@echo running isort...;
	pipenv run isort -rc -c -df;
	@echo running flake8...;
	pipenv run flake8 --max-complexity 10 --ignore E501,D401
.PHONY: local-lint
