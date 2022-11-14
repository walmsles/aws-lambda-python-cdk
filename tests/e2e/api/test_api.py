from typing import Dict

import pytest
from requests import Request

from tests.e2e.api.infrastructure import EVENT_API_URL
from tests.utils.fetcher import fetch_http_response


@pytest.fixture()
def event_api_url(infrastructure: Dict) -> str:
    print(infrastructure)
    return infrastructure.get(EVENT_API_URL)


def test_event_api(event_api_url):
    # Given
    api_data = {"body": "Hello World"}
    status_code = 200

    # When
    response = fetch_http_response(
        Request(
            method="POST",
            url=f"{event_api_url}events",
            json={"body": api_data},
        )
    )
    api_response: Dict = response.json()

    # Then
    # ** we should get a 200 status code and "transaction_id" will be returned in the API response.
    assert response.status_code == status_code
    assert api_response.get("transaction_id", "Not Found") != "Not Found"
