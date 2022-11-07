import json
from typing import Dict

import boto3
import pytest
from mypy_boto3_s3 import S3Client

from tests.utils.fetcher import fetch_lambda_response, fetch_test_event


@pytest.fixture()
def event_api_lambda_arn(infrastructure: Dict) -> str:
    return infrastructure.get("EventApiFunctionArn")


@pytest.fixture()
def event_bucket_name(infrastructure: Dict) -> str:
    return infrastructure.get("EventStoreBucket")


def test_event_api(event_api_lambda_arn, event_bucket_name):
    # Given
    transaction_id = "8cfe08aa-51e9-49cf-8cd6-c00d415bfa97"
    api_gw_event = fetch_test_event("event_api_gw.json")
    api_data = {"body": "Hello World"}

    # When
    fetch_lambda_response(event_api_lambda_arn, payload=json.dumps(api_gw_event))
    s3_client: S3Client = boto3.client("s3")

    # should be able to read from the S3 bucket and get thge event body
    # using the requestId from the event payload
    event_object = s3_client.get_object(
        Bucket=event_bucket_name, Key=f"{transaction_id}.json"
    )
    event_data = json.loads(event_object.get("Body").read().decode("utf-8"))

    # Then
    # ** we should read the actual data injected by the API from S3.
    assert event_data == api_data
