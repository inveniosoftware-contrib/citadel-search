#!/bin/bash

# check python version
if [[ "$(python --version)" =~ "Python ${PYTHON_VERSION}" ]]; then
    echo Python ${PYTHON_VERSION} is installed
else
    echo Python ${PYTHON_VERSION} is not installed. Aborting.
    exit 1;
fi

# check pipenv installed
if [[ "$(pipenv --version)" =~ "pipenv, version" ]]; then
    echo pipenv is installed
else
    echo pipenv is not installed. Aborting.
    exit 1;
fi
