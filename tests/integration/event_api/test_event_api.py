from typing import Dict

import pytest


@pytest.fixture()
def event_api_lambda_arn(infrastructure: Dict) -> str:
    print(infrastructure)
    return infrastructure.get("EventApiFunctionArn")


def test_event_api():

    print("Testing Event API stack")
