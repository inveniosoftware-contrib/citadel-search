# Utility for debug purposes: Replace which package/module you want to replace
readonly LOCATION=$(pip show invenio-records-rest | grep Location | awk '{print $2}')
readonly SCRIPT_PATH=$(dirname $0)

rm -f ${LOCATION}/invenio_records_rest/views.py
cp ${SCRIPT_PATH}/views.py ${LOCATION}/invenio_records_rest/views.py
