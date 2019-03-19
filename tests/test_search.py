import json

import pytest
import requests

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": ''
}


@pytest.mark.unit
def test_search(endpoint, api_key):
    """
    Test search over public documents. Test that the ``_access.*`` field is
    not searched over.
    """
    HEADERS['Authorization'] = 'Bearer {credentials}'.format(credentials=api_key)

    body = {
        "_access": {
            "owner": ["CernSearch-Administrators@cern.ch"],
            "update": ["CernSearch-Administrators@cern.ch"],
            "delete": ["CernSearch-Administrators@cern.ch"]
        },
        "_data": {
            "title": "Test default search field",
            "description": "This contains CernSearch and should appear"
        },
        "$schema": "{endpoint}/schemas/test/doc_v0.0.2.json".format(
            endpoint=endpoint
        )
    }

    # Create first test record
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json()['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == 'Test default search field'
    assert resp_data.get('description') == 'This contains CernSearch and should appear'

    control_number_one = resp_body.get("control_number")

    # Create second test record
    body["_data"]['description'] = 'This does not contains the magic word and should not appear'

    # Create test record
    resp = requests.post('{endpoint}/api/records/'.format(endpoint=endpoint),
                         headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 201

    # Check non presence of OCR content in DB record
    resp_body = resp.json()['metadata']
    assert resp_body.get('control_number') is not None
    resp_data = resp_body.get("_data")
    assert resp_data.get('title') == 'Test default search field'
    assert resp_data.get('description') == 'This does not contains the magic word and should not appear'

    control_number_two = resp_body.get("control_number")

    # # Needed to allow ES to process the file
    import time
    time.sleep(1)
    # Search records
    # Test search with no query
    resp = requests.get('{endpoint}/api/records/'.format(endpoint=endpoint),
                        headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 2

    resp = requests.get('{endpoint}/api/records/?q=CernSearch'
                        .format(endpoint=endpoint),
                        headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 200

    resp_hits = resp.json()['hits']
    assert resp_hits.get('total') == 1

    description = resp_hits['hits'][0]['metadata'].get("_data").get('description')
    assert description is not None
    assert description == 'This contains CernSearch and should appear'

    # Clean the instance. Delete record
    resp = requests.delete('{endpoint}/api/record/{control_number}'
                           .format(endpoint=endpoint, control_number=control_number_one),
                           headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 204

    resp = requests.delete('{endpoint}/api/record/{control_number}'
                           .format(endpoint=endpoint, control_number=control_number_two),
                           headers=HEADERS, data=json.dumps(body))

    assert resp.status_code == 204
