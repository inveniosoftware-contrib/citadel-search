# check python version
if [[ "$(python --version)" =~ "Python ${PYTHON_VERSION}" ]]; then
    echo Python ${PYTHON_VERSION} is installed
else
    echo Python ${PYTHON_VERSION} is not installed. Aborting.
    exit 1;
fi

# check poetry installed
if [[ "$(poetry --version)" =~ "poetry, version" ]]; then
    echo poetry is installed
else
    echo poetry is not installed. Aborting.
    exit 1;
fi
