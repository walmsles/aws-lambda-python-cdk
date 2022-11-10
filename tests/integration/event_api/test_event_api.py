import json
from typing import Dict

import boto3
import pytest
from mypy_boto3_s3 import S3Client
from mypy_boto3_sqs import SQSClient

from tests.integration.event_api.infrastructure import (
    EVENT_API_FUNCTION_ARN,
    EVENT_MESSAGE_QUEUE,
    EVENT_STORE_BUCKET,
)
from tests.utils.fetcher import fetch_lambda_response, fetch_test_event


@pytest.fixture()
def event_api_lambda_arn(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_API_FUNCTION_ARN)


@pytest.fixture()
def event_bucket_name(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_STORE_BUCKET)


@pytest.fixture()
def event_message_queue(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_MESSAGE_QUEUE)


def test_event_api(event_api_lambda_arn, event_bucket_name, event_message_queue):
    # Given
    transaction_id = "8cfe08aa-51e9-49cf-8cd6-c00d415bfa97"
    api_gw_event = fetch_test_event("event_api_gw.json")
    api_data = {"body": "Hello World"}

    # When
    lambda_response = fetch_lambda_response(
        event_api_lambda_arn, payload=json.dumps(api_gw_event)
    )
    response = lambda_response[0]
    s3_client: S3Client = boto3.client("s3")
    sqs_client: SQSClient = boto3.client("sqs")

    # Raise exception oj Lambda function handler failure
    if response.get("FunctionError"):
        message = json.loads(response.get("Payload").read().decode("utf-8"))
        raise Exception(message)

    # should be able to read from the S3 bucket and get thge event body
    # using the requestId from the event payload
    event_object = s3_client.get_object(
        Bucket=event_bucket_name, Key=f"{transaction_id}.json"
    )
    event_data = json.loads(event_object.get("Body").read().decode("utf-8"))

    # read 1 message from the Queue which will be ther esince
    # is a synchronous lambda call
    the_messages = sqs_client.receive_message(
        QueueUrl=event_message_queue, WaitTimeSeconds=10, MaxNumberOfMessages=1
    )
    message_data = the_messages.get("Messages", [])
    if len(message_data) != 1:
        raise Exception("No message found in SQS")

    message_body = json.loads(message_data[0].get("Body", ""))

    # Then
    # ** we should read the actual data injected by the API from S3.
    assert event_data == api_data
    assert message_body.get("body") == api_data
    assert message_body.get("message_id") == transaction_id
