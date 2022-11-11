import json
from typing import Dict

import boto3
import pytest
from mypy_boto3_dynamodb import DynamoDBClient

from tests.integration.event_processor.infrastructure import (
    EVENT_API_FUNCTION_ARN,
    EVENT_MESSAGE_QUEUE,
    EVENT_STORE_TABLE,
)
from tests.utils.fetcher import fetch_lambda_response, fetch_test_event


@pytest.fixture()
def event_api_lambda_arn(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_API_FUNCTION_ARN)


@pytest.fixture()
def event_message_queue(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_MESSAGE_QUEUE)


@pytest.fixture()
def event_storage_table(infrastructure: Dict) -> str:
    return infrastructure.get(EVENT_STORE_TABLE)


def test_event_api(event_storage_table, event_api_lambda_arn):
    # Given
    message_id = "message-111-XXX"
    content = {"key1": "value1"}
    sqs_event = fetch_test_event("event_processor_sqs.json")

    # When We pass an SQS event to Lambda
    #
    lambda_response = fetch_lambda_response(
        event_api_lambda_arn, payload=json.dumps(sqs_event)
    )
    response = lambda_response[0]

    # Raise exception on Lambda function handler failure
    if response.get("FunctionError"):
        message = json.loads(response.get("Payload").read().decode("utf-8"))
        raise Exception(message)

    # Read item from the table to test the Integration
    ddb_client: DynamoDBClient = boto3.resource("dynamodb")
    table = ddb_client.Table(event_storage_table)
    table_item = table.get_item(Key={"message_id": message_id})
    item = table_item.get("Item")

    # Then
    assert item.get("body") == content
    assert item.get("message_id") == message_id
