import pytest
import requests


@pytest.mark.unit
def test_default_search_field(endpoint, api_key):

    # Check the UI does not generate 50X Errors
    resp = requests.post('{endpoint}/account/settings/applications/'.format(
        endpoint=endpoint))

    assert resp.status_code == 200
